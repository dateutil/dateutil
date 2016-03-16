# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ._common import unittest, TZWinContext

from datetime import datetime, timedelta
from datetime import time as dt_time
from six import BytesIO, StringIO

import os
import subprocess
import sys
import time as _time
import base64
IS_WIN = sys.platform.startswith('win')

# dateutil imports
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil import tz as tz
from dateutil import zoneinfo

try:
    from dateutil import tzwin
except ImportError as e:
    if IS_WIN:
        raise e
    else:
        pass

MISSING_TARBALL = ("This test fails if you don't have the dateutil "
                   "timezone file installed. Please read the README")

TZFILE_EST5EDT = b"""
VFppZgAAAAAAAAAAAAAAAAAAAAAAAAAEAAAABAAAAAAAAADrAAAABAAAABCeph5wn7rrYKCGAHCh
ms1gomXicKOD6eCkaq5wpTWnYKZTyvCnFYlgqDOs8Kj+peCqE47wqt6H4KvzcPCsvmngrdNS8K6e
S+CvszTwsH4t4LGcUXCyZ0pgs3wzcLRHLGC1XBVwticOYLc793C4BvBguRvZcLnm0mC7BPXwu8a0
YLzk1/C9r9DgvsS58L+PsuDApJvwwW+U4MKEffDDT3bgxGRf8MUvWODGTXxwxw864MgtXnDI+Fdg
yg1AcMrYOWDLiPBw0iP0cNJg++DTdeTw1EDd4NVVxvDWIL/g1zWo8NgAoeDZFYrw2eCD4Nr+p3Db
wGXg3N6JcN2pgmDevmtw34lkYOCeTXDhaUZg4n4vcONJKGDkXhFw5Vcu4OZHLfDnNxDg6CcP8OkW
8uDqBvHw6vbU4Ovm0/Ds1rbg7ca18O6/02Dvr9Jw8J+1YPGPtHDyf5dg82+WcPRfeWD1T3hw9j9b
YPcvWnD4KHfg+Q88cPoIWeD6+Fjw++g74PzYOvD9yB3g/rgc8P+n/+AAl/7wAYfh4AJ34PADcP5g
BGD9cAVQ4GAGQN9wBzDCYAeNGXAJEKRgCa2U8ArwhmAL4IVwDNmi4A3AZ3AOuYTgD6mD8BCZZuAR
iWXwEnlI4BNpR/AUWSrgFUkp8BY5DOAXKQvwGCIpYBkI7fAaAgtgGvIKcBvh7WAc0exwHcHPYB6x
znAfobFgIHYA8CGBk2AiVeLwI2qv4CQ1xPAlSpHgJhWm8Ccqc+An/sNwKQpV4CnepXAq6jfgK76H
cCzTVGAtnmlwLrM2YC9+S3AwkxhgMWdn8DJy+mAzR0nwNFLcYDUnK/A2Mr5gNwcN8Dgb2uA45u/w
Ofu84DrG0fA7257gPK/ucD27gOA+j9BwP5ti4EBvsnBBhH9gQk+UcENkYWBEL3ZwRURDYEYPWHBH
JCVgR/h08EkEB2BJ2FbwSuPpYEu4OPBMzQXgTZga8E6s5+BPd/zwUIzJ4FFhGXBSbKvgU0D7cFRM
jeBVIN1wVixv4FcAv3BYFYxgWOChcFn1bmBawINwW9VQYFypn/BdtTJgXomB8F+VFGBgaWPwYX4w
4GJJRfBjXhLgZCkn8GU99OBmEkRwZx3W4GfyJnBo/bjgadIIcGrdmuBrsepwbMa3YG2RzHBupplg
b3GucHCGe2BxWsrwcmZdYHM6rPB0Rj9gdRqO8HYvW+B2+nDweA894HjaUvB57x/gero08HvPAeB8
o1Fwfa7j4H6DM3B/jsXgAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAgMBAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEA
AQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAf//x8ABAP//ubAABP//x8ABCP//x8ABDEVEVABFU1QARVdU
AEVQVAAAAAABAAAAAQ==
"""

EUROPE_HELSINKI = b"""
VFppZgAAAAAAAAAAAAAAAAAAAAAAAAAFAAAABQAAAAAAAAB1AAAABQAAAA2kc28Yy85RYMy/hdAV
I+uQFhPckBcDzZAX876QGOOvkBnToJAaw5GQG7y9EBysrhAdnJ8QHoyQEB98gRAgbHIQIVxjECJM
VBAjPEUQJCw2ECUcJxAmDBgQJwVDkCf1NJAo5SWQKdUWkCrFB5ArtPiQLKTpkC2U2pAuhMuQL3S8
kDBkrZAxXdkQMnK0EDM9uxA0UpYQNR2dEDYyeBA2/X8QOBuUkDjdYRA5+3aQOr1DEDvbWJA8pl+Q
Pbs6kD6GQZA/mxyQQGYjkEGEORBCRgWQQ2QbEEQl55BFQ/0QRgXJkEcj3xBH7uYQSQPBEEnOyBBK
46MQS66qEEzMv5BNjowQTqyhkE9ubhBQjIOQUVeKkFJsZZBTN2yQVExHkFUXTpBWLCmQVvcwkFgV
RhBY1xKQWfUoEFq29JBb1QoQXKAREF207BBef/MQX5TOEGBf1RBhfeqQYj+3EGNdzJBkH5kQZT2u
kGYItZBnHZCQZ+iXkGj9cpBpyHmQat1UkGuoW5BsxnEQbYg9kG6mUxBvaB+QcIY1EHFRPBByZhcQ
czEeEHRF+RB1EQAQdi8VkHbw4hB4DveQeNDEEHnu2ZB6sKYQe867kHyZwpB9rp2QfnmkkH+Of5AC
AQIDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQD
BAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAME
AwQAABdoAAAAACowAQQAABwgAAkAACowAQQAABwgAAlITVQARUVTVABFRVQAAAAAAQEAAAABAQ==
"""

NEW_YORK = b"""
VFppZgAAAAAAAAAAAAAAAAAAAAAAAAAEAAAABAAAABcAAADrAAAABAAAABCeph5wn7rrYKCGAHCh
ms1gomXicKOD6eCkaq5wpTWnYKZTyvCnFYlgqDOs8Kj+peCqE47wqt6H4KvzcPCsvmngrdNS8K6e
S+CvszTwsH4t4LGcUXCyZ0pgs3wzcLRHLGC1XBVwticOYLc793C4BvBguRvZcLnm0mC7BPXwu8a0
YLzk1/C9r9DgvsS58L+PsuDApJvwwW+U4MKEffDDT3bgxGRf8MUvWODGTXxwxw864MgtXnDI+Fdg
yg1AcMrYOWDLiPBw0iP0cNJg++DTdeTw1EDd4NVVxvDWIL/g1zWo8NgAoeDZFYrw2eCD4Nr+p3Db
wGXg3N6JcN2pgmDevmtw34lkYOCeTXDhaUZg4n4vcONJKGDkXhFw5Vcu4OZHLfDnNxDg6CcP8OkW
8uDqBvHw6vbU4Ovm0/Ds1rbg7ca18O6/02Dvr9Jw8J+1YPGPtHDyf5dg82+WcPRfeWD1T3hw9j9b
YPcvWnD4KHfg+Q88cPoIWeD6+Fjw++g74PzYOvD9yB3g/rgc8P+n/+AAl/7wAYfh4AJ34PADcP5g
BGD9cAVQ4GEGQN9yBzDCYgeNGXMJEKRjCa2U9ArwhmQL4IV1DNmi5Q3AZ3YOuYTmD6mD9xCZZucR
iWX4EnlI6BNpR/kUWSrpFUkp+RY5DOoXKQv6GCIpaxkI7fsaAgtsGvIKfBvh7Wwc0ex8HcHPbR6x
zn0fobFtIHYA/SGBk20iVeL+I2qv7iQ1xP4lSpHuJhWm/ycqc+8n/sOAKQpV8CnepYAq6jfxK76H
gSzTVHItnmmCLrM2cy9+S4MwkxhzMWdoBDJy+nQzR0oENFLcdTUnLAU2Mr51NwcOBjgb2vY45vAG
Ofu89jrG0gY72572PK/uhj27gPY+j9CGP5ti9kBvsoZBhH92Qk+UhkNkYXZEL3aHRURDd0XzqQdH
LV/3R9OLB0kNQfdJs20HSu0j90uciYdM1kB3TXxrh062IndPXE2HUJYEd1E8L4dSdeZ3UxwRh1RV
yHdU+/OHVjWqd1blEAdYHsb3WMTyB1n+qPdapNQHW96K91yEtgddvmz3XmSYB1+eTvdgTbSHYYdr
d2ItlodjZ013ZA14h2VHL3dl7VqHZycRd2fNPIdpBvN3aa0eh2rm1XdrljsHbM/x9212HQdur9P3
b1X/B3CPtfdxNeEHcm+X93MVwwd0T3n3dP7fh3Y4lnd23sGHeBh4d3i+o4d5+Fp3ep6Fh3vYPHd8
fmeHfbged35eSYd/mAB3AAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAgMBAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEA
AQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAf//x8ABAP//ubAABP//x8ABCP//x8ABDEVEVABFU1QARVdU
AEVQVAAEslgAAAAAAQWk7AEAAAACB4YfggAAAAMJZ1MDAAAABAtIhoQAAAAFDSsLhQAAAAYPDD8G
AAAABxDtcocAAAAIEs6mCAAAAAkVn8qJAAAACheA/goAAAALGWIxiwAAAAwdJeoMAAAADSHa5Q0A
AAAOJZ6djgAAAA8nf9EPAAAAECpQ9ZAAAAARLDIpEQAAABIuE1ySAAAAEzDnJBMAAAAUM7hIlAAA
ABU2jBAVAAAAFkO3G5YAAAAXAAAAAQAAAAE=
"""

TZICAL_EST5EDT = """
BEGIN:VTIMEZONE
TZID:US-Eastern
LAST-MODIFIED:19870101T000000Z
TZURL:http://zones.stds_r_us.net/tz/US-Eastern
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
END:DAYLIGHT
END:VTIMEZONE
"""


class TZTest(unittest.TestCase):
    def testStrStart1(self):
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr("EST5EDT")).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr("EST5EDT")).tzname(), "EDT")

    def testStrEnd1(self):
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tz.tzstr("EST5EDT")).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tz.tzstr("EST5EDT")).tzname(), "EST")

    def testStrStart2(self):
        s = "EST5EDT,4,0,6,7200,10,0,26,7200,3600"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")

    def testStrEnd2(self):
        s = "EST5EDT,4,0,6,7200,10,0,26,7200,3600"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")

    def testStrStart3(self):
        s = "EST5EDT,4,1,0,7200,10,-1,0,7200,3600"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")

    def testStrEnd3(self):
        s = "EST5EDT,4,1,0,7200,10,-1,0,7200,3600"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")

    def testStrStart4(self):
        s = "EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")

    def testStrEnd4(self):
        s = "EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")

    def testStrStart5(self):
        s = "EST5EDT4,95/02:00:00,298/02:00"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")

    def testStrEnd5(self):
        s = "EST5EDT4,95/02:00:00,298/02"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")

    def testStrStart6(self):
        s = "EST5EDT4,J96/02:00:00,J299/02:00"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")

    def testStrEnd6(self):
        s = "EST5EDT4,J96/02:00:00,J299/02"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tz.tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tz.tzstr(s)).tzname(), "EST")

    def testStrStr(self):
        # Test that tz.tzstr() won't throw an error if given a str instead
        # of a unicode literal.
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tz.tzstr(str("EST5EDT"))).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tz.tzstr(str("EST5EDT"))).tzname(), "EDT")

    def testStrCmp1(self):
        self.assertEqual(tz.tzstr("EST5EDT"),
                         tz.tzstr("EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"))

    def testStrCmp2(self):
        self.assertEqual(tz.tzstr("EST5EDT"),
                         tz.tzstr("EST5EDT,4,1,0,7200,10,-1,0,7200,3600"))

    def testRangeCmp1(self):
        from dateutil.relativedelta import SU
        self.assertEqual(tz.tzstr("EST5EDT"),
                         tz.tzrange("EST", -18000, "EDT", -14400,
                                 relativedelta(hours=+2,
                                               month=4, day=1,
                                               weekday=SU(+1)),
                                 relativedelta(hours=+1,
                                               month=10, day=31,
                                               weekday=SU(-1))))

    def testRangeCmp2(self):
        self.assertEqual(tz.tzstr("EST5EDT"),
                         tz.tzrange("EST", -18000, "EDT"))

    def testFileStart1(self):
        tzc = tz.tzfile(BytesIO(base64.b64decode(TZFILE_EST5EDT)))
        self.assertEqual(datetime(2003, 4, 6, 1, 59, tzinfo=tzc).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00, tzinfo=tzc).tzname(), "EDT")

    def testFileEnd1(self):
        tzc = tz.tzfile(BytesIO(base64.b64decode(TZFILE_EST5EDT)))
        self.assertEqual(datetime(2003, 10, 26, 0, 59, tzinfo=tzc).tzname(),
                         "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00, tzinfo=tzc).tzname(),
                         "EST")

    def testZoneInfoFileStart1(self):
        tz = zoneinfo.gettz("EST5EDT")
        self.assertEqual(datetime(2003, 4, 6, 1, 59, tzinfo=tz).tzname(), "EST",
                         MISSING_TARBALL)
        self.assertEqual(datetime(2003, 4, 6, 2, 00, tzinfo=tz).tzname(), "EDT")

    def testZoneInfoFileEnd1(self):
        tzc = zoneinfo.gettz("EST5EDT")
        self.assertEqual(datetime(2003, 10, 26, 0, 59, tzinfo=tzc).tzname(),
                         "EDT", MISSING_TARBALL)
        self.assertEqual(datetime(2003, 10, 26, 1, 00, tzinfo=tzc).tzname(),
                         "EST")

    def testZoneInfoOffsetSignal(self):
        utc = zoneinfo.gettz("UTC")
        nyc = zoneinfo.gettz("America/New_York")
        self.assertNotEqual(utc, None, MISSING_TARBALL)
        self.assertNotEqual(nyc, None)
        t0 = datetime(2007, 11, 4, 0, 30, tzinfo=nyc)
        t1 = t0.astimezone(utc)
        t2 = t1.astimezone(nyc)
        self.assertEqual(t0, t2)
        self.assertEqual(nyc.dst(t0), timedelta(hours=1))

    def testTzNameNone(self):
        gmt5 = tz.tzoffset(None, -18000)       # -5:00
        self.assertIs(datetime(2003, 10, 26, 0, 0, tzinfo=gmt5).tzname(),
                      None)

    def testICalStart1(self):
        tzc = tz.tzical(StringIO(TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003, 4, 6, 1, 59, tzinfo=tzc).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00, tzinfo=tzc).tzname(), "EDT")

    def testICalEnd1(self):
        tzc = tz.tzical(StringIO(TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003, 10, 26, 0, 59, tzinfo=tzc).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00, tzinfo=tzc).tzname(), "EST")

    def testRoundNonFullMinutes(self):
        # This timezone has an offset of 5992 seconds in 1900-01-01.
        tzc = tz.tzfile(BytesIO(base64.b64decode(EUROPE_HELSINKI)))
        self.assertEqual(str(datetime(1900, 1, 1, 0, 0, tzinfo=tzc)),
                             "1900-01-01 00:00:00+01:40")

    def testLeapCountDecodesProperly(self):
        # This timezone has leapcnt, and failed to decode until
        # Eugene Oden notified about the issue.

        # As leap information is currently unused (and unstored) by tzfile() we
        # can only indirectly test this: Take advantage of tzfile() not closing
        # the input file if handed in as an opened file and assert that the
        # full file content has been read by tzfile(). Note: For this test to
        # work NEW_YORK must be in TZif version 1 format i.e. no more data
        # after TZif v1 header + data has been read
        fileobj = BytesIO(base64.b64decode(NEW_YORK))
        tzc = tz.tzfile(fileobj)
        # we expect no remaining file content now, i.e. zero-length; if there's
        # still data we haven't read the file format correctly
        remaining_tzfile_content = fileobj.read()
        self.assertEqual(len(remaining_tzfile_content), 0)

    def testIsStd(self):
        # NEW_YORK tzfile contains this isstd information:
        isstd_expected = (0, 0, 0, 1)
        tzc = tz.tzfile(BytesIO(base64.b64decode(NEW_YORK)))
        # gather the actual information as parsed by the tzfile class
        isstd = []
        for ttinfo in tzc._ttinfo_list:
            # ttinfo objects contain boolean values
            isstd.append(int(ttinfo.isstd))
        # ttinfo list may contain more entries than isstd file content
        isstd = tuple(isstd[:len(isstd_expected)])
        self.assertEqual(
            isstd_expected, isstd,
            "isstd UTC/local indicators parsed: %s != tzfile contents: %s"
            % (isstd, isstd_expected))

    def testGettz(self):
        # bug 892569
        str(tz.gettz('UTC'))

    def testGetTzEquality(self):
        self.assertEqual(tz.gettz('UTC'), tz.gettz('UTC'))

    def testBrokenIsDstHandling(self):
        # tzrange._isdst() was using a date() rather than a datetime().
        # Issue reported by Lennart Regebro.
        dt = datetime(2007, 8, 6, 4, 10, tzinfo=tz.tzutc())
        self.assertEqual(dt.astimezone(tz=tz.gettz("GMT+2")),
                          datetime(2007, 8, 6, 6, 10, tzinfo=tz.tzstr("GMT+2")))

    def testGMTHasNoDaylight(self):
        # tz.tzstr("GMT+2") improperly considered daylight saving time.
        # Issue reported by Lennart Regebro.
        dt = datetime(2007, 8, 6, 4, 10)
        self.assertEqual(tz.gettz("GMT+2").dst(dt), timedelta(0))

    def testGMTOffset(self):
        # GMT and UTC offsets have inverted signal when compared to the
        # usual TZ variable handling.
        dt = datetime(2007, 8, 6, 4, 10, tzinfo=tz.tzutc())
        self.assertEqual(dt.astimezone(tz=tz.tzstr("GMT+2")),
                          datetime(2007, 8, 6, 6, 10, tzinfo=tz.tzstr("GMT+2")))
        self.assertEqual(dt.astimezone(tz=tz.gettz("UTC-2")),
                          datetime(2007, 8, 6, 2, 10, tzinfo=tz.tzstr("UTC-2")))

    def testTimeOnlyUTC(self):
        # https://github.com/dateutil/dateutil/issues/132
        # tzutc doesn't care
        tz_utc = tz.tzutc()
        self.assertEqual(dt_time(13, 20, tzinfo=tz_utc).utcoffset(),
                         timedelta(0))

    def testTimeOnlyOffset(self):
        # tzoffset doesn't care
        tz_offset = tz.tzoffset('+3', 3600)
        self.assertEqual(dt_time(13, 20, tzinfo=tz_offset).utcoffset(),
                         timedelta(seconds=3600))

    def testTimeOnlyLocal(self):
        # tzlocal returns None
        tz_local = tz.tzlocal()
        self.assertIs(dt_time(13, 20, tzinfo=tz_local).utcoffset(), None)

    def testTimeOnlyRange(self):
        # tzrange returns None
        tz_range = tz.tzrange('dflt')
        self.assertIs(dt_time(13, 20, tzinfo=tz_range).utcoffset(), None)

    def testTimeOnlyGettz(self):
        # gettz returns None
        tz_get = tz.gettz('Europe/Minsk')
        self.assertIs(dt_time(13, 20, tzinfo=tz_get).utcoffset(), None)

    @unittest.skipIf(IS_WIN, "requires Unix")
    def testTZSetDoesntCorrupt(self):
        # if we start in non-UTC then tzset UTC make sure parse doesn't get
        # confused
        os.environ['TZ'] = 'UTC'
        _time.tzset()
        # this should parse to UTC timezone not the original timezone
        dt = parse('2014-07-20T12:34:56+00:00')
        self.assertEqual(str(dt), '2014-07-20 12:34:56+00:00')


@unittest.skipUnless(IS_WIN, "Requires Windows")
class TzWinTest(unittest.TestCase):
    def testTzResLoadName(self):
        # This may not work right on non-US locales.
        tzr = tzwin.tzres()
        self.assertEqual(tzr.load_name(112), "Eastern Standard Time")

    def testTzResNameFromString(self):
        tzr = tzwin.tzres()
        self.assertEqual(tzr.name_from_string('@tzres.dll,-221'),
                         'Alaskan Daylight Time')

        self.assertEqual(tzr.name_from_string('Samoa Daylight Time'),
                         'Samoa Daylight Time')

        with self.assertRaises(ValueError):
            tzr.name_from_string('@tzres.dll,100')

    def testIsdstZoneWithNoDaylightSaving(self):
        tz = tzwin.tzwin("UTC")
        dt = parse("2013-03-06 19:08:15")
        self.assertFalse(tz._isdst(dt))

    def testOffset(self):
        tz = tzwin.tzwin("Cape Verde Standard Time")
        self.assertEqual(tz.utcoffset(datetime(1995, 5, 21, 12, 9, 13)),
                         timedelta(-1, 82800))

    def testLocal(self):
        # Not sure how to pin a local time zone, so for now we're just going
        # to run this and make sure it doesn't raise an error
        # See Github Issue #135: https://github.com/dateutil/dateutil/issues/135
        datetime.now(tzwin.tzwinlocal())

        datetime(2014, 3, 11, tzinfo=tzwin.tzwinlocal()).utcoffset()

    def testTzwinName(self):
        # https://github.com/dateutil/dateutil/issues/143
        tw = tz.tzwin('Eastern Standard Time')

        # Cover the transitions for at least two years.
        ESTs = 'Eastern Standard Time'
        EDTs = 'Eastern Daylight Time'
        transition_dates = [(datetime(2015, 3, 8, 0, 59), ESTs),
                            (datetime(2015, 3, 8, 2, 1), EDTs),
                            (datetime(2015, 11, 1, 1, 59), EDTs),
                            (datetime(2015, 11, 1, 3, 1), ESTs),
                            (datetime(2016, 3, 13, 0, 59), ESTs),
                            (datetime(2016, 3, 13, 2, 1), EDTs),
                            (datetime(2016, 11, 6, 1, 59), EDTs),
                            (datetime(2016, 11, 6, 3, 1), ESTs)]

        for t_date, expected in transition_dates:
            self.assertEqual(t_date.replace(tzinfo=tw).tzname(), expected)

    def testTzwinRepr(self):
        tw = tz.tzwin('Yakutsk Standard Time')
        self.assertEqual(repr(tw), 'tzwin(' +
                                   repr('Yakutsk Standard Time') + ')')

    def testTzWinEquality(self):
        # https://github.com/dateutil/dateutil/issues/151
        tzwin_names = ('Eastern Standard Time',
                       'West Pacific Standard Time',
                       'Yakutsk Standard Time',
                       'Iran Standard Time',
                       'UTC')

        for tzwin_name in tzwin_names:
            # Get two different instances to compare
            tw1 = tz.tzwin(tzwin_name)
            tw2 = tz.tzwin(tzwin_name)

            self.assertEqual(tw1, tw2)

    def testTzWinInequality(self):
        # https://github.com/dateutil/dateutil/issues/151
        # Note these last two currently differ only in their name.
        tzwin_names = (('Eastern Standard Time', 'Yakutsk Standard Time'),
                       ('Greenwich Standard Time', 'GMT Standard Time'),
                       ('GMT Standard Time', 'UTC'),
                       ('E. South America Standard Time',
                        'Argentina Standard Time'))

        for tzwn1, tzwn2 in tzwin_names:
            # Get two different instances to compare            
            tw1 = tz.tzwin(tzwn1)
            tw2 = tz.tzwin(tzwn2)

            self.assertNotEqual(tw1, tw2)

    def testTzwinTimeOnlyDST(self):
        # For zones with DST, .dst() should return None
        tw_est = tz.tzwin('Eastern Standard Time')
        self.assertIs(dt_time(14, 10, tzinfo=tw_est).dst(), None)

        # This zone has no DST, so .dst() can return 0
        tw_sast = tz.tzwin('South Africa Standard Time')
        self.assertEqual(dt_time(14, 10, tzinfo=tw_sast).dst(),
                         timedelta(0))

    def testTzwinTimeOnlyUTCOffset(self):
        # For zones with DST, .utcoffset() should return None
        tw_est = tz.tzwin('Eastern Standard Time')
        self.assertIs(dt_time(14, 10, tzinfo=tw_est).utcoffset(), None)

        # This zone has no DST, so .utcoffset() returns standard offset
        tw_sast = tz.tzwin('South Africa Standard Time')
        self.assertEqual(dt_time(14, 10, tzinfo=tw_sast).utcoffset(),
                         timedelta(hours=2))

    def testTzwinLocalTimeOnlyTZName(self):
        # For zones with DST, the name defaults to standard time
        tw_est = tz.tzwin('Eastern Standard Time')
        self.assertEqual(dt_time(14, 10, tzinfo=tw_est).tzname(),
                         'Eastern Standard Time')

        # For zones with no DST, this should work normally.
        tw_sast = tz.tzwin('South Africa Standard Time')
        self.assertEqual(dt_time(14, 10, tzinfo=tw_sast),
                         'South Africa Standard Time')

    @unittest.skipUnless(TZWinContext.tz_change_allowed(),
        'Skipping unless tz changes are allowed.')
    def testTzwinLocalName(self):
        # https://github.com/dateutil/dateutil/issues/143
        ESTs = 'Eastern Standard Time'
        EDTs = 'Eastern Daylight Time'
        transition_dates = [(datetime(2015, 3, 8, 0, 59), ESTs),
                            (datetime(2015, 3, 8, 2, 1), EDTs),
                            (datetime(2015, 11, 1, 1, 59), EDTs),
                            (datetime(2015, 11, 1, 3, 1), ESTs),
                            (datetime(2016, 3, 13, 0, 59), ESTs),
                            (datetime(2016, 3, 13, 2, 1), EDTs),
                            (datetime(2016, 11, 6, 1, 59), EDTs),
                            (datetime(2016, 11, 6, 3, 1), ESTs)]

        with TZWinContext('Eastern Standard Time'):
            tw = tz.tzwinlocal()

            for t_date, expected in transition_dates:
                self.assertEqual(t_date.replace(tzinfo=tw).tzname(), expected)

    def testTzWinLocalRepr(self):
        tw = tz.tzwinlocal()
        self.assertEqual(repr(tw), 'tzwinlocal()')

    @unittest.skipUnless(TZWinContext.tz_change_allowed(),
        'Skipping unless tz changes are allowed.')
    def testTzwinLocalRepr(self):
        # https://github.com/dateutil/dateutil/issues/143
        with TZWinContext('Eastern Standard Time'):
            tw = tz.tzwinlocal()

            self.assertEqual(str(tw), 'tzwinlocal(' +
                                      repr('Eastern Standard Time') + ')')

        with TZWinContext('Pacific Standard Time'):
            tw = tz.tzwinlocal()

            self.assertEqual(str(tw), 'tzwinlocal(' + 
                                      repr('Pacific Standard Time') + ')')

    @unittest.skipUnless(TZWinContext.tz_change_allowed(),
        'Skipping unless tz changes are allowed.')
    def testTzwinLocalEquality(self):
        tw_est = tz.tzwin('Eastern Standard Time')
        tw_pst = tz.tzwin('Pacific Standard Time')

        with TZWinContext('Eastern Standard Time'):
            twl1 = tz.tzwinlocal()
            twl2 = tz.tzwinlocal()

            self.assertEqual(twl1, twl2)
            self.assertEqual(twl1, tw_est)
            self.assertNotEqual(twl1, tw_pst)

        with TZWinContext('Pacific Standard Time'):
            twl1 = tz.tzwinlocal()
            twl2 = tz.tzwinlocal()
            tw = tz.tzwin('Pacific Standard Time')

            self.assertEqual(twl1, twl2)
            self.assertEqual(twl1, tw)
            self.assertEqual(twl1, tw_pst)
            self.assertNotEqual(twl1, tw_est)

    @unittest.skipUnless(TZWinContext.tz_change_allowed(),
        'Skipping unless tz changes are allowed.')
    def testTzwinLocalTimeOnlyDST(self):
        # For zones with DST, .dst() should return None
        with TZWinContext('Eastern Standard Time'):
            twl = tz.tzwinlocal()
            self.assertIs(dt_time(14, 10, tzinfo=twl).dst(), None)

        # This zone has no DST, so .dst() can return 0
        with TZWinContext('South Africa Standard Time'):
            twl = tz.tzwinlocal()
            self.assertEqual(dt_time(14, 10, tzinfo=twl).dst(), timedelta(0))

    @unittest.skipUnless(TZWinContext.tz_change_allowed(),
        'Skipping unless tz changes are allowed.')
    def testTzwinLocalTimeOnlyUTCOffset(self):
        # For zones with DST, .utcoffset() should return None
        with TZWinContext('Eastern Standard Time'):
            twl = tz.tzwinlocal()
            self.assertIs(dt_time(14, 10, tzinfo=twl).utcoffset(), None)

        # This zone has no DST, so .utcoffset() returns standard offset
        with TZWinContext('South Africa Standard Time'):
            twl = tz.tzwinlocal()
            self.assertEqual(dt_time(14, 10, tzinfo=twl).utcoffset(),
                             timedelta(hours=2))

    @unittest.skipUnless(TZWinContext.tz_change_allowed(),
        'Skipping unless tz changes are allowed.')
    def testTzwinLocalTimeOnlyTZName(self):
        # For zones with DST, the name defaults to standard time
        with TZWinContext('Eastern Standard Time'):
            twl = tz.tzwinlocal()
            self.assertEqual(dt_time(14, 10, tzinfo=twl).tzname(),
                             'Eastern Standard Time')

        # For zones with no DST, this should work normally.
        with TZWinContext('South Africa Standard Time'):
            twl = tz.tzwinlocal()
            self.assertEqual(dt_time(14, 10, tzinfo=twl).tzname(),
                             'South Africa Standard Time')

