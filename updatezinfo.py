#!/usr/bin/env python
import os
import hashlib
import json
import io

from six.moves.urllib import request

from dateutil.zoneinfo import rebuild

METADATA_FILE = "zonefile_metadata.json"


def main():
    with io.open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)

    if not os.path.isfile(metadata['tzdata_file']):
        print("Downloading tz file from iana")
        request.urlretrieve(os.path.join(metadata['releases_url'],
                                         metadata['tzdata_file']),
                            metadata['tzdata_file'])
    with open(metadata['tzdata_file'], 'rb') as tzfile:
        sha_hasher = hashlib.sha512()
        sha_hasher.update(tzfile.read())
        sha_512_file = sha_hasher.hexdigest()
        assert metadata['tzdata_file_sha512'] == sha_512_file, "SHA failed for"
    print("Updating timezone information...")
    rebuild(metadata['tzdata_file'], zonegroups=metadata['zonegroups'])
    print("Done.")

if __name__ == "__main__":
    main()
