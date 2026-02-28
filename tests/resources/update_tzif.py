# /// script
# dependencies = [
#   "requests",
# ]
# ///

import argparse
import asyncio
import base64
import gzip
import json
import logging
import os
import pathlib
import shutil
import struct
import subprocess
import tempfile
import urllib.parse
from collections.abc import Mapping
from typing import Final

import requests

IANA_LATEST_LOCATION: Final[str] = (
    "https://www.iana.org/time-zones/repository/tzdb-latest.tar.lz"
)
SOURCE: Final[str] = "https://data.iana.org/time-zones/releases"
DATA_DIR: Final[pathlib.Path] = pathlib.Path("tests/resources/data")


def _is_tzif(fpath: pathlib.Path) -> bool:
    if fpath.is_dir():
        return False
    with open(fpath, "rb") as f:
        magic = f.read(4)
    return magic == b"TZif"


def _parse_filename_from_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    filename = parsed_url.path.rsplit("/", 1)[-1]

    return filename


async def download_tzdb(
    working_dir: pathlib.Path,
    url: str = IANA_LATEST_LOCATION,
) -> pathlib.Path:
    """Download the tzdata and tzcode tarballs."""

    filename = _parse_filename_from_url(url)
    r = requests.get(url, allow_redirects=True, stream=True)
    download_location = working_dir / filename

    logging.info(
        "Downloaded %s from %s to %s", filename, url, download_location
    )

    with open(download_location, "wb") as f:
        f.write(r.raw.read())

    return download_location


async def unpack_tzdb_tarball(
    download_location: pathlib.Path,
    output_dir: pathlib.Path | None = None,
    cwd: pathlib.Path | None = None,
) -> pathlib.Path:
    logging.info("Unpacking %s to %s", download_location, output_dir)
    if cwd is None:
        cwd = pathlib.Path.cwd()

    if output_dir is None:
        output_dir = cwd / "tzdb"

    output_dir.mkdir()
    await asyncio.to_thread(
        subprocess.run,
        [
            "tar",
            "--lzip",
            "-xf",
            os.fspath(download_location.absolute()),
            "-C",
            os.fspath(output_dir),
        ],
        cwd=cwd,
        check=True,
    )

    # The tzdb tarball has for some reason a top-level directory called
    # tzdb-..., which is annoying to deal with. We will delete that and
    # unpack its contents into `output_dir`
    for i, subdir in list(enumerate(output_dir.glob("tzdb-*"))):
        if i > 1:
            raise ValueError("TZDB directory contains more than one subdir")
        for p in subdir.iterdir():
            p.rename(output_dir / p.name)
        subdir.rmdir()

    return output_dir


async def _file_to_v1(tzif_file: pathlib.Path, out_path: pathlib.Path) -> None:
    # Make sure that the parents exist
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure that this is a valid TZif file
    contents = tzif_file.read_bytes()
    if contents[0:4] != b"TZif":
        raise ValueError(f"Invalid TZif data found! {tzif_file}")
    version = int(contents[4:5])

    header_start = 4 + 16
    header_end = header_start + 24  # 6l == 24 bytes
    if version < 2:
        logging.warn(
            "Version 1 file found, no conversion necessary (%s)", tzif_file
        )
        shutil.copyfile(tzif_file, out_path)
        return

    isutcnt, isstdcnt, leapcnt, timecnt, typecnt, charcnt = struct.unpack(
        ">6l", contents[header_start:header_end]
    )

    file_size = (
        timecnt * 5 + typecnt * 6 + charcnt + leapcnt * 8 + isstdcnt + isutcnt
    )
    file_size += header_end
    out = b"TZif" + b"\x00" + contents[5:file_size]

    if contents[file_size : (file_size + 4)] != b"TZif":
        raise ValueError(
            f"Version 2 file not truncated at Version 2 header: {tzif_file}"
        )

    out_path.write_bytes(out)


async def tzif_files_to_v1(
    input_base_path: pathlib.Path, output_base_path: pathlib.Path
) -> None:
    tasks = []
    for tzif_in_file in filter(_is_tzif, input_base_path.rglob("*")):
        tzif_v1_file = output_base_path / tzif_in_file.relative_to(
            input_base_path
        )
        tasks.append(
            asyncio.create_task(_file_to_v1(tzif_in_file, tzif_v1_file))
        )

    asyncio.gather(*tasks)


async def make_tzdb_install(
    install_dir: pathlib.Path, cwd: pathlib.Path, slim: bool
) -> None:
    cmd = ["make", f"DESTDIR={os.fspath(install_dir)}"]
    if slim:
        cmd.append("ZFLAGS=-b slim")
    else:
        cmd.append("ZFLAGS=-b fat")

    cmd.append("install")

    await asyncio.to_thread(
        subprocess.run,
        cmd,
        check=True,
        cwd=cwd,
    )


def file_to_text(tzif_file: pathlib.Path) -> str:
    """Compress the file with gzip and base64 encode."""
    tzif_data = tzif_file.read_bytes()
    compressed_data = gzip.compress(tzif_data)
    b64_data = base64.b64encode(compressed_data).decode("utf-8")
    return b64_data


def zonefile_to_json(
    data_root: pathlib.Path, json_outfile: pathlib.Path, keys: frozenset[str]
) -> None:
    out_data = {}
    for dirpath, dirnames, filenames in data_root.walk():
        for file in filenames:
            filepath = dirpath / file
            tzkey = str(filepath.relative_to(data_root))
            if tzkey not in keys:
                continue
            out_data[tzkey] = file_to_text(dirpath / file)
    json_outfile.write_text(json.dumps(out_data, sort_keys=True, indent=2))


def read_required_keys(loc: pathlib.Path) -> frozenset[str]:
    json_str = loc.read_text()
    return frozenset(json.loads(json_str))


async def main() -> None:
    required_keys = read_required_keys(DATA_DIR / "keys.json")

    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)
        download_location = await download_tzdb(working_dir=tdp)
        tzdata_dir = tdp / "tzdb"
        V1_OUT = tdp / "v1"
        V2P_OUT = tdp / "v2p_fat"
        V2P_OUT_SLIM = tdp / "v2p_slim"
        await unpack_tzdb_tarball(
            download_location, cwd=tdp, output_dir=tzdata_dir
        )
        v2p_fat_future = make_tzdb_install(V2P_OUT, cwd=tzdata_dir, slim=False)
        v2p_slim_future = make_tzdb_install(
            V2P_OUT_SLIM, cwd=tzdata_dir, slim=True
        )
        V2P_ZONEINFO = V2P_OUT / "usr/share/zoneinfo"
        V2P_SLIM_ZONEINFO = V2P_OUT_SLIM / "usr/share/zoneinfo"
        await v2p_fat_future
        v1_future = tzif_files_to_v1(V2P_OUT / "usr/share/zoneinfo", V1_OUT)
        await asyncio.gather(v2p_slim_future, v1_future)
        zonefile_to_json(
            V1_OUT, DATA_DIR / "zoneinfo_v1.json", keys=required_keys
        )
        zonefile_to_json(
            V2P_ZONEINFO, DATA_DIR / "zoneinfo_slim.json", keys=required_keys
        )
        zonefile_to_json(
            V2P_SLIM_ZONEINFO,
            DATA_DIR / "zoneinfo_fat.json",
            keys=required_keys,
        )


if __name__ == "__main__":
    asyncio.run(main())
