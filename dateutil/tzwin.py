# This code was kindly provided by Jeffrey Harris.
import _winreg
import struct
import datetime

TIMEZONESKEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones"
TIMEZONEINFOKEY = r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation"
HANDLE = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
LOCALKEY = _winreg.OpenKey(HANDLE, TIMEZONEINFOKEY)
TZPARENT = _winreg.OpenKey(HANDLE, TIMEZONESKEY)
TZPARENTSIZE = _winreg.QueryInfoKey(TZPARENT)[0]
ONEWEEK = datetime.timedelta(7)

class tzwin(datetime.tzinfo):
    """tzinfo class based on win32's timezones available in the registry.
    
    >>> local = tzwin('Central Standard Time')
    >>> oct1 = datetime.datetime(month=10, year=2004, day=1, tzinfo=local)
    >>> dec1 = datetime.datetime(month=12, year=2004, day=1, tzinfo=local)
    >>> oct1.dst()
    datetime.timedelta(0, 3600)
    >>> dec1.dst()
    datetime.timedelta(0)
    >>> braz = tzwin('E. South America Standard Time')
    >>> braz.dst(oct1)
    datetime.timedelta(0)
    >>> braz.dst(dec1)
    datetime.timedelta(0, 3600)
    
    """
    def __init__(self, name):
        self._info = _tzwininfo(name)
        
    def utcoffset(self, dt):
        if self._isdst(dt):
            return datetime.timedelta(minutes=self._info.dstoffset)
        else:
            return datetime.timedelta(minutes=self._info.stdoffset)

    def dst(self, dt):
        if self._isdst(dt):
            minutes = self._info.dstoffset - self._info.stdoffset
            return datetime.timedelta(minutes=minutes)
        else:
            return datetime.timedelta(0)
        
    def tzname(self, dt):
        if self._isdst(dt):
            return self._info.dstname
        else:
            return self._info.stdname

    def list():
        """Return a list of all time zones known to the system."""
        return [_winreg.EnumKey(TZPARENT, i) for i in range(TZPARENTSIZE)]
    list = staticmethod(list)
    
    def _isdst(self, dt):
        i = self._info
        dston = picknthweekday(dt.year, i.dstmonth, i.dstdayofweek,
                               i.dsthour, i.dstminute, i.dstweeknumber)
        dstoff = picknthweekday(dt.year, i.stdmonth, i.stddayofweek,
                                i.stdhour, i.stdminute, i.stdweeknumber)
        if dston < dstoff:
            return dston <= dt.replace(tzinfo=None) < dstoff
        else:
            return not dstoff <= dt.replace(tzinfo=None) < dston

    def __repr__(self):
        return "tzwin(%s)" % repr(self._info.display)
    
    __reduce__ = object.__reduce__

class _tzwininfo(object):
    """Read a registry key for a timezone, expose its contents."""
    
    def __init__(self, path):
        """Load path, or if path is empty, load local time."""
        if path:
            keydict=valuestodict(_winreg.OpenKey(TZPARENT, path))
            self.display = keydict['Display']
            self.dstname = keydict['Dlt']
            self.stdname = keydict['Std']
            
            #see http://ww_winreg.jsiinc.com/SUBA/tip0300/rh0398.htm
            tup = struct.unpack('=3l16h', keydict['TZI'])
            self.stdoffset = -tup[0]-tup[1] #Bias + StandardBias * -1
            self.dstoffset = self.stdoffset - tup[2] # + DaylightBias * -1
            
            offset=3
            self.stdmonth = tup[1 + offset]
            self.stddayofweek = tup[2 + offset] #Sunday=0
            self.stdweeknumber = tup[3 + offset] #Last = 5
            self.stdhour = tup[4 + offset]
            self.stdminute = tup[5 + offset]
            
            offset=11
            self.dstmonth = tup[1 + offset]
            self.dstdayofweek = tup[2 + offset] #Sunday=0
            self.dstweeknumber = tup[3 + offset] #Last = 5
            self.dsthour = tup[4 + offset]
            self.dstminute = tup[5 + offset]
            
        else:
            keydict=valuestodict(LOCALKEY)
            
            self.stdname = keydict['StandardName']
            self.dstname = keydict['DaylightName']
            
            sourcekey=_winreg.OpenKey(TZPARENT, self.stdname)
            self.display = valuestodict(sourcekey)['Display']
            
            self.stdoffset = -keydict['Bias']-keydict['StandardBias']
            self.dstoffset = self.stdoffset - keydict['DaylightBias']

            #see http://ww_winreg.jsiinc.com/SUBA/tip0300/rh0398.htm
            tup = struct.unpack('=8h', keydict['StandardStart'])

            offset=0
            self.stdmonth = tup[1 + offset]
            self.stddayofweek = tup[2 + offset] #Sunday=0
            self.stdweeknumber = tup[3 + offset] #Last = 5
            self.stdhour = tup[4 + offset]
            self.stdminute = tup[5 + offset]
            
            tup = struct.unpack('=8h', keydict['DaylightStart'])
            self.dstmonth = tup[1 + offset]
            self.dstdayofweek = tup[2 + offset] #Sunday=0
            self.dstweeknumber = tup[3 + offset] #Last = 5
            self.dsthour = tup[4 + offset]
            self.dstminute = tup[5 + offset]

def picknthweekday(year, month, dayofweek, hour, minute, whichweek):
    """dayofweek == 0 means Sunday, whichweek 5 means last instance"""
    first = datetime.datetime(year, month, 1, hour, minute)
    weekdayone = first.replace(day=((dayofweek-first.isoweekday())%7+1))
    for n in xrange(whichweek):
        dt = weekdayone+(whichweek-n)*ONEWEEK
        if dt.month == month:
            return dt

def valuestodict(key):
    """Convert a registry key's values to a dictionary."""
    dict={}
    size=_winreg.QueryInfoKey(key)[1]
    for i in xrange(size):
        dict[_winreg.EnumValue(key, i)[0]]=_winreg.EnumValue(key, i)[1]
    return dict

def _test():
    import tzwin, doctest
    doctest.testmod(tzwin, verbose=0)

if __name__ == '__main__':
    _test()
