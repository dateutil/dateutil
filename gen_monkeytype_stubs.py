from pathlib import Path
from pprint import pprint
import subprocess


SRC_DIR = Path("dateutil")
TEST_DIR = Path("dateutil/test")
EXCLUDE_SUBDIRS = {"test"}
EXCLUDE_FILES = {"_version.py"}


def module_name_from_path(path):
    if path.parts[-1] == "__init__.py":
        path = path.parent
    return str(path).replace("/", ".").rstrip(".py")


def main():
    old_db = Path("monkeytype.sqlite3")
    if old_db.exists():
        old_db.unlink()

    subprocess.run(["monkeytype", "run", "-m", "pytest", str(TEST_DIR)])

    module_paths = [
        p
        for p in SRC_DIR.glob("**/*.py")
        if p.parts[1] not in EXCLUDE_SUBDIRS
        and p.parts[-1] not in EXCLUDE_FILES
    ]

    modules = {module_name_from_path(p): Path(str(p) + "i") for p in module_paths}
    for mod, output in modules.items():
        subprocess.run(f"monkeytype stub {mod} > {output}", shell=True)
        # remove empty output files
        if output.stat().st_size == 0:
            output.unlink()


if __name__ == "__main__":
    main()
