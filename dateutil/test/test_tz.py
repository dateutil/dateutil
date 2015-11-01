# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
from six import BytesIO, StringIO

import sys
import base64
import unittest
IS_WIN = sys.platform.startswith('win')

# dateutil imports
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.tz import *
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
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EDT")

    def testStrEnd1(self):
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EST")

    def testStrStart2(self):
        s = "EST5EDT,4,0,6,7200,10,0,26,7200,3600"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd2(self):
        s = "EST5EDT,4,0,6,7200,10,0,26,7200,3600"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart3(self):
        s = "EST5EDT,4,1,0,7200,10,-1,0,7200,3600"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd3(self):
        s = "EST5EDT,4,1,0,7200,10,-1,0,7200,3600"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart4(self):
        s = "EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd4(self):
        s = "EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart5(self):
        s = "EST5EDT4,95/02:00:00,298/02:00"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd5(self):
        s = "EST5EDT4,95/02:00:00,298/02"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart6(self):
        s = "EST5EDT4,J96/02:00:00,J299/02:00"
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd6(self):
        s = "EST5EDT4,J96/02:00:00,J299/02"
        self.assertEqual(datetime(2003, 10, 26, 0, 59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStr(self):
        # Test that tzstr() won't throw an error if given a str instead
        # of a unicode literal.
        self.assertEqual(datetime(2003, 4, 6, 1, 59,
                                  tzinfo=tzstr(str("EST5EDT"))).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00,
                                  tzinfo=tzstr(str("EST5EDT"))).tzname(), "EDT")

    def testStrCmp1(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzstr("EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"))

    def testStrCmp2(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzstr("EST5EDT,4,1,0,7200,10,-1,0,7200,3600"))

    def testRangeCmp1(self):
        from dateutil.relativedelta import SU
        self.assertEqual(tzstr("EST5EDT"),
                         tzrange("EST", -18000, "EDT", -14400,
                                 relativedelta(hours=+2,
                                               month=4, day=1,
                                               weekday=SU(+1)),
                                 relativedelta(hours=+1,
                                               month=10, day=31,
                                               weekday=SU(-1))))

    def testRangeCmp2(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzrange("EST", -18000, "EDT"))

    def testFileStart1(self):
        tz = tzfile(BytesIO(base64.b64decode(TZFILE_EST5EDT)))
        self.assertEqual(datetime(2003, 4, 6, 1, 59, tzinfo=tz).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00, tzinfo=tz).tzname(), "EDT")

    def testFileEnd1(self):
        tz = tzfile(BytesIO(base64.b64decode(TZFILE_EST5EDT)))
        self.assertEqual(datetime(2003, 10, 26, 0, 59, tzinfo=tz).tzname(),
                         "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00, tzinfo=tz).tzname(),
                         "EST")

    def testZoneInfoFileStart1(self):
        tz = zoneinfo.gettz("EST5EDT")
        self.assertEqual(datetime(2003, 4, 6, 1, 59, tzinfo=tz).tzname(), "EST",
                         MISSING_TARBALL)
        self.assertEqual(datetime(2003, 4, 6, 2, 00, tzinfo=tz).tzname(), "EDT")

    def testZoneInfoFileEnd1(self):
        tz = zoneinfo.gettz("EST5EDT")
        self.assertEqual(datetime(2003, 10, 26, 0, 59, tzinfo=tz).tzname(),
                         "EDT", MISSING_TARBALL)
        self.assertEqual(datetime(2003, 10, 26, 1, 00, tzinfo=tz).tzname(),
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
        gmt5 = tzoffset(None, -18000)       # -5:00
        self.assertIs(datetime(2003, 10, 26, 0, 0, tzinfo=gmt5).tzname(),
                      None)


    def testICalStart1(self):
        tz = tzical(StringIO(TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003, 4, 6, 1, 59, tzinfo=tz).tzname(), "EST")
        self.assertEqual(datetime(2003, 4, 6, 2, 00, tzinfo=tz).tzname(), "EDT")

    def testICalEnd1(self):
        tz = tzical(StringIO(TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003, 10, 26, 0, 59, tzinfo=tz).tzname(), "EDT")
        self.assertEqual(datetime(2003, 10, 26, 1, 00, tzinfo=tz).tzname(), "EST")

    def testRoundNonFullMinutes(self):
        # This timezone has an offset of 5992 seconds in 1900-01-01.
        tz = tzfile(BytesIO(base64.b64decode(EUROPE_HELSINKI)))
        self.assertEqual(str(datetime(1900, 1, 1, 0, 0, tzinfo=tz)),
                             "1900-01-01 00:00:00+01:40")

    def testLeapCountDecodesProperly(self):
        # This timezone has leapcnt, and failed to decode until
        # Eugene Oden notified about the issue.
        tz = tzfile(BytesIO(base64.b64decode(NEW_YORK)))
        self.assertEqual(datetime(2007, 3, 31, 20, 12).tzname(), None)

    def testGettz(self):
        # bug 892569
        str(gettz('UTC'))

    def testBrokenIsDstHandling(self):
        # tzrange._isdst() was using a date() rather than a datetime().
        # Issue reported by Lennart Regebro.
        dt = datetime(2007, 8, 6, 4, 10, tzinfo=tzutc())
        self.assertEqual(dt.astimezone(tz=gettz("GMT+2")),
                          datetime(2007, 8, 6, 6, 10, tzinfo=tzstr("GMT+2")))

    def testGMTHasNoDaylight(self):
        # tzstr("GMT+2") improperly considered daylight saving time.
        # Issue reported by Lennart Regebro.
        dt = datetime(2007, 8, 6, 4, 10)
        self.assertEqual(gettz("GMT+2").dst(dt), timedelta(0))

    def testGMTOffset(self):
        # GMT and UTC offsets have inverted signal when compared to the
        # usual TZ variable handling.
        dt = datetime(2007, 8, 6, 4, 10, tzinfo=tzutc())
        self.assertEqual(dt.astimezone(tz=tzstr("GMT+2")),
                          datetime(2007, 8, 6, 6, 10, tzinfo=tzstr("GMT+2")))
        self.assertEqual(dt.astimezone(tz=gettz("UTC-2")),
                          datetime(2007, 8, 6, 2, 10, tzinfo=tzstr("UTC-2")))

    @unittest.skipIf(IS_WIN, "requires Unix")
    def testTZSetDoesntCorrupt(self):
        # if we start in non-UTC then tzset UTC make sure parse doesn't get
        # confused
        os.environ['TZ'] = 'UTC'
        _time.tzset()
        # this should parse to UTC timezone not the original timezone
        dt = parse('2014-07-20T12:34:56+00:00')
        self.assertEqual(str(dt), '2014-07-20 12:34:56+00:00')

@unittest.skipIf(not IS_WIN, "Requires Windows")
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