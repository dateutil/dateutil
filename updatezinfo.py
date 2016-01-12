#!/usr/bin/env python
import os
import hashlib
import json
import io

from six.moves.urllib import request

from dateutil.zoneinfo import rebuild

from time import sleep

MAX_RETRIES = 1 #iana FTP server is sometimes overloaded
WAIT_SEC = 6

METADATA_FILE = "zonefile_metadata.json"


def main():
    with io.open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)

    if not os.path.isfile(metadata['tzdata_file']):
        print("Downloading tz file from iana")
        attempts = 0

        while attempts <= MAX_RETRIES:
            try:
                request.urlretrieve(os.path.join(metadata['releases_url'],
                                                 metadata['tzdata_file']),
                                    metadata['tzdata_file'])
                break #success!
            except IOError as e:
                attempts += 1
                if attempts > MAX_RETRIES:
                    raise
                #otherwise, loop & retry
                msg = 'Retrying download, in (%s) sec... (error: "%s")'
                print( msg % (WAIT_SEC, e))
                sleep(WAIT_SEC)
    with open(metadata['tzdata_file'], 'rb') as tzfile:
        sha_hasher = hashlib.sha512()
        sha_hasher.update(tzfile.read())
        sha_512_file = sha_hasher.hexdigest()
        assert metadata['tzdata_file_sha512'] == sha_512_file, "SHA failed for"
    print("Updating timezone information...")
    rebuild.rebuild(metadata['tzdata_file'], zonegroups=metadata['zonegroups'],
            metadata=metadata)
    print("Done.")

if __name__ == "__main__":
    main()
