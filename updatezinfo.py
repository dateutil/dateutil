#!/usr/bin/python
from dateutil.zoneinfo import rebuild
import shutil
import sys
import os
import re

SERVER = "elsie.nci.nih.gov"
DIR = "/pub"
NAME = re.compile("tzdata(.*).tar.gz")

def main():
    if len(sys.argv) == 2:
        tzdata = sys.argv[1]
    else:
        from ftplib import FTP
        print "Connecting to %s..." % SERVER
        ftp = FTP(SERVER)
        print "Logging in..."
        ftp.login()
        print "Changing to %s..." % DIR
        ftp.cwd(DIR)
        print "Listing files..."
        for name in ftp.nlst():
            if NAME.match(name):
                break
        else:
            sys.exit("error: file matching %s not found" % NAME.pattern)
        if os.path.isfile(name):
            print "Found local %s..." % name
        else:
            print "Retrieving %s..." % name
            file = open(name, "w")
            ftp.retrbinary("RETR "+name, file.write)
            file.close()
        ftp.close()
        tzdata = name
    if not tzdata or not NAME.match(tzdata):
        sys.exit("Usage: updatezinfo.py tzdataXXXXX.tar.gz")
    print "Updating timezone information..."
    rebuild(tzdata, NAME.match(tzdata).group(1))
    print "Done."

if __name__ == "__main__":
    main()
