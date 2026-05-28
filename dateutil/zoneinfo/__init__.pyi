from io import BytesIO
from typing import (
    Dict,
    List,
    Optional,
    Union,
)
from dateutil.tz import tzfile


ZONEFILENAME: str
METADATA_FN: str


def get_zonefile_instance(new_instance: bool = False) -> ZoneInfoFile: ...


def gettz(name: str) -> tzfile: ...


def gettz_db_metadata() -> Dict[str, Union[float, List[str], str]]: ...


def getzoneinfofile_stream() -> BytesIO: ...


class ZoneInfoFile:
    def __init__(self, zonefile_stream: Optional[BytesIO] = None) -> None: ...
    def get(self, name: str, default: None = None) -> Optional[tzfile]: ...
