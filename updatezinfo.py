#!/usr/bin/env python
import os
import hashlib

from six.moves.urllib import request

from dateutil.zoneinfo import rebuild


# ad-hoc solution. TODO: use configuration file or something
TZRELEASES = "ftp://ftp.iana.org/tz/releases/"
TZFILEPATTERN = "tzdata{tag}.tar.gz"
TZTAG = "2014j"
SHA512 = "4c2979be3a96f91f8576304ec905d571b73df0842c8300c1d7317819b45ab3e29948ed911aa265b12a4ad587d5cba44f646dd02e40e4fbf9e68556a2d327142e"

TZFILE = TZFILEPATTERN.format(tag=TZTAG)

def main():
    if not os.path.isfile(TZFILE):
        print("Downloading tz file from iana")
        request.urlretrieve(TZRELEASES + TZFILE, TZFILE)
    with open(TZFILE,'rb') as tzfile:
        sha_hasher = hashlib.sha512()
        sha_hasher.update(tzfile.read())
        sha_512_file = sha_hasher.hexdigest()
        assert SHA512 == sha_512_file, "SHA failed for downloaded tz file"
    print("Updating timezone information...")
    rebuild(TZFILE, TZTAG)
    print("Done.")

if __name__ == "__main__":
    main()
