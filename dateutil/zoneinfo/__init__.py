# -*- coding: utf-8 -*-
import logging
import os
import re
import warnings
import tempfile
import shutil
from subprocess import check_call
from tarfile import TarFile
from pkgutil import get_data
from io import BytesIO
from contextlib import closing

from dateutil.tz import tzfile

__all__ = ["setcachesize", "gettz", "gettz_db_version", "rebuild"]

_ZONEFILENAME = "dateutil-zoneinfo.tar.gz"
_VERSIONFNAME = ".version"
_VERSIONLABEL = "version"

# python2.6 compatability. Note that TarFile.__exit__ != TarFile.close, but
# it's close enough for python2.6
_tar_open = TarFile.open
if not hasattr(TarFile, '__exit__'):
    def _tar_open(*args, **kwargs):
        return closing(TarFile.open(*args, **kwargs))


class tzfile(tzfile):
    def __reduce__(self):
        return (gettz, (self._filename,))


def getzoneinfofile_stream():
    try:
        return BytesIO(get_data(__name__, _ZONEFILENAME))
    except IOError as e:  # TODO  switch to FileNotFoundError?
        warnings.warn("I/O error({0}): {1}".format(e.errno, e.strerror))
        return None


def gettz_db_version(zonefile_stream=None):
    """
    Retrieve the version of a ZoneInfoFile that has been built with a .version
    file containing "version=the_version", as output by rebuild().

    :returns:
        Returns a version string or `None` if no version was found.
    """
    if zonefile_stream is None:
        zonefile_stream = getzoneinfofile_stream()

    with _tar_open(fileobj=zonefile_stream, mode='r') as tf:
        try:
            vf = tf.extractfile(tf.getmember(_VERSIONFNAME))
            for line in vf:
                lsplit = line.split('=')
                if lsplit[0] == _VERSIONLABEL:
                    return lsplit[1]
        except KeyError:
            pass

    return None


class ZoneInfoFile(object):
    def __init__(self, zonefile_stream=None):
        if zonefile_stream is not None:
            with _tar_open(fileobj=zonefile_stream, mode='r') as tf:
                # dict comprehension does not work on python2.6
                # TODO: get back to the nicer syntax when we ditch python2.6
                # self.zones = {zf.name: tzfile(tf.extractfile(zf),
                #               filename = zf.name)
                #              for zf in tf.getmembers() if zf.isfile()}
                self.zones = dict((zf.name, tzfile(tf.extractfile(zf),
                                                   filename=zf.name))
                                  for zf in tf.getmembers()
                                  if zf.isfile() and zf.name != _VERSIONFNAME)

                # deal with links: They'll point to their parent object. Less
                # waste of memory
                # links = {zl.name: self.zones[zl.linkname]
                #        for zl in tf.getmembers() if zl.islnk() or zl.issym()}
                links = dict((zl.name, self.zones[zl.linkname])
                             for zl in tf.getmembers() if
                             zl.islnk() or zl.issym())
                self.zones.update(links)
        else:
            self.zones = dict()


# The current API has gettz as a module function, although in fact it taps into
# a stateful class. So as a workaround for now, without changing the API, we
# will create a new "global" class instance the first time a user requests a
# timezone. Ugly, but adheres to the api.
#
# TODO: deprecate this.
_CLASS_ZONE_INSTANCE = list()


def gettz(name):
    if len(_CLASS_ZONE_INSTANCE) == 0:
        _CLASS_ZONE_INSTANCE.append(ZoneInfoFile(getzoneinfofile_stream()))
    return _CLASS_ZONE_INSTANCE[0].zones.get(name)


def rebuild(filename, tag=None, format="gz", zonegroups=[], version=None):
    """Rebuild the internal timezone info in dateutil/zoneinfo/zoneinfo*tar*

    filename is the timezone tarball from ftp.iana.org/tz.

    """
    tmpdir = tempfile.mkdtemp()
    zonedir = os.path.join(tmpdir, "zoneinfo")
    moduledir = os.path.dirname(__file__)
    try:
        with _tar_open(filename) as tf:
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

        # Write the version of the database used to a file in our
        # rebuilt tarball
        version_floc = os.path.join(tmpdir, _VERSIONFNAME)
        if version is None:
            # If version is not specified, try to infer it from the filename
            m = re.match(".*?tzdata(?P<vnum>.*?)\.tar\.gz", filename)
            if m is not None:
                version = m.group('vnum')

        if version is not None:
            # If we have a version, write it to a hidden file
            with open(version_floc, "w") as vfile:
                vfile.write('{label}={value}'.format(label=_VERSIONLABEL,
                                                     value=version))

        target = os.path.join(moduledir, _ZONEFILENAME)
        with _tar_open(target, "w:%s" % format) as tf:
            if os.path.exists(version_floc):
                tf.add(version_floc, _VERSIONFNAME)

            for entry in os.listdir(zonedir):
                entrypath = os.path.join(zonedir, entry)
                tf.add(entrypath, entry)
    finally:
        shutil.rmtree(tmpdir)
