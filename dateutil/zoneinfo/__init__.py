# -*- coding: utf-8 -*-
import logging
import os
import warnings
from subprocess import check_call
from tarfile import TarFile
from pkgutil import get_data
from io import BytesIO

from dateutil.tz import tzfile

__all__ = ["setcachesize", "gettz", "rebuild"]

_ZONEFILENAME = "dateutil-zoneinfo.tar.gz"

class tzfile(tzfile):
    def __reduce__(self):
        return (gettz, (self._filename,))

def getzoneinfofile_stream():
    try:
        return BytesIO(get_data(__name__, _ZONEFILENAME))
    except IOError as e: # TODO  switch to FileNotFoundError?
        warnings.warn("I/O error({0}): {1}".format(e.errno, e.strerror))
        return None

class ZoneInfoFile(object):
    def __init__(self, zonefile_stream=None):
        if zonefile_stream is not None:
            with TarFile.open(fileobj=zonefile_stream,mode='r') as tf:
                self.zones = {zf.name: tzfile(tf.extractfile(zf), filename = zf.name)
                              for zf in tf.getmembers() if zf.isfile()}
                # deal with links: They'll point to their parent object. Less waste of memory
                links = {zl.name: self.zones[zl.linkname]
                         for zl in tf.getmembers() if zl.islnk() or zl.issym()}
                self.zones.update(links)
        else:
            self.zones = dict()

_CLASS_ZONE_INSTANCE = ZoneInfoFile(getzoneinfofile_stream())
def gettz(name):
    return _CLASS_ZONE_INSTANCE.zones.get(name)



def rebuild(filename, tag=None, format="gz",zonegroups=[]):
    """Rebuild the internal timezone info in dateutil/zoneinfo/zoneinfo*tar*

    filename is the timezone tarball from ftp.iana.org/tz.

    """
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    zonedir = os.path.join(tmpdir, "zoneinfo")
    moduledir = os.path.dirname(__file__)
    try:
        with TarFile.open(filename) as tf:
            # The "backwards" zone file contains links to other files, so must be
            # processed as last
            for name in zonegroups:
                tf.extract(name, tmpdir)
            filepaths = [os.path.join(tmpdir, n) for n in zonegroups]
            try:
                check_call(["zic", "-d", zonedir] + filepaths)
            except OSError as e:
                if e.errno == 2:
                    logging.error(
                        "Could not find zic. Perhaps you need to install "
                        "libc-bin or some other package that provides it, "
                        "or it's not in your PATH?")
                    raise
        target = os.path.join(moduledir, _ZONEFILENAME)
        with TarFile.open(target, "w:%s" % format) as tf:
            for entry in os.listdir(zonedir):
                entrypath = os.path.join(zonedir, entry)
                tf.add(entrypath, entry)
    finally:
        shutil.rmtree(tmpdir)
