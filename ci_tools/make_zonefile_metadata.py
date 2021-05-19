#!/usr/bin/env python3

import hashlib

ZONEFILE_METADATA_TEMPLATE = """{{
    "metadata_version": 2.0,
    "releases_url": [],
    "tzdata_file": "{tzdata_file}",
    "tzdata_file_sha512": "{tzdata_sha512}",
    "tzversion": "{tzdata_version}",
    "zonegroups": [
        "africa",
        "antarctica",
        "asia",
        "australasia",
        "europe",
        "northamerica",
        "southamerica",
        "etcetera",
        "factory",
        "backzone",
        "backward"
    ]
}}
"""


def calculate_sha512(fpath):
    with open(fpath, 'rb') as f:
        sha_hasher = hashlib.sha512()
        sha_hasher.update(f.read())
        return sha_hasher.hexdigest()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('tzdata', metavar='TZDATA',
                        help='The name tzdata tarball file')
    parser.add_argument('version', metavar='VERSION',
                        help='The version of the tzdata tarball')
    parser.add_argument('out', metavar='OUT', nargs='?',
                        default='zonefile_metadata.json',
                        help='Where to write the file')

    args = parser.parse_args()

    tzdata = args.tzdata
    version = args.version
    sha512 = calculate_sha512(tzdata)

    metadata_file_text = ZONEFILE_METADATA_TEMPLATE.format(
        tzdata_file=tzdata,
        tzdata_version=version,
        tzdata_sha512=sha512,
    )

    with open(args.out, 'w') as f:
        f.write(metadata_file_text)

