import datetime
import calendar

M366MASK = tuple([1]*31+[2]*29+[3]*31+[4]*30+[5]*31+[6]*30+
                 [7]*31+[8]*31+[9]*30+[10]*31+[11]*30+[12]*31)
M365MASK = list(M366MASK)
M29, M30, M31 = range(1,30), range(1,31), range(1,32)
MDAY366MASK = tuple(M31+M29+M31+M30+M31+M30+M31+M31+M30+M31+M30+M31)
MDAY365MASK = list(MDAY366MASK)
M366RANGE = (0,31,60,91,121,152,182,213,244,274,305,335,366)
M365RANGE = (0,31,59,90,120,151,181,212,243,273,304,334,365)
WDAYMASK = (0,1,2,3,4,5,6)*54
del M29, M30, M31, M365MASK[59], MDAY365MASK[59]
MDAY365MASK = tuple(MDAY365MASK)
M365MASK = tuple(M365MASK)

(FREQ_YEARLY,
 FREQ_MONTHLY,
 FREQ_WEEKLY,
 FREQ_DAILY,
 FREQ_HOURLY,
 FREQ_MINUTELY,
 FREQ_SECONDLY) = range(7)

# Imported on demand.
easter = None
parser = None

class weekday(object):
    __slots__ = ["weekday", "n"]

    def __init__(self, weekday, n=0):
        self.weekday = weekday
        self.n = n

    def __call__(self, n):
        if n == self.n:
            return self
        else:
            return self.__class__(self.weekday, n)

    def __eq__(self, other):
        try:
            if self.weekday != other.weekday or self.n != other.n:
                return False
        except AttributeError:
            return False
        return True

    def __repr__(self):
        s = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")[self.weekday]
        if not self.n:
            return s
        else:
            return "%s(%+d)" % (s, self.n)

MO, TU, WE, TH, FR, SA, SU = weekdays = tuple([weekday(x) for x in range(7)])

class rrule:
    def __init__(self, freq, dtstart=None,
                 interval=1, wkst=0, count=None, until=None, bysetpos=None,
                 bymonth=None, bymonthday=None, byyearday=None, byeaster=None,
                 byweekno=None, byweekday=None,
                 byhour=None, byminute=None, bysecond=None):
        if not dtstart:
            dtstart = datetime.datetime.now()
        self._dtstart = dtstart
        self._tzinfo = dtstart.tzinfo
        self._freq = freq
        self._interval = interval
        self._count = count
        self._until = until
        if type(wkst) is int:
            self._wkst = wkst
        else:
            self._wkst = wkst.weekday
        if bysetpos is None:
            self._bysetpos = None
        elif type(bysetpos) is int:
            self._bysetpos = (bysetpos,)
        else:
            self._bysetpos = tuple(bysetpos)
        if not (bymonth or byweekno or byyearday or bymonthday or
                byweekday is not None or byeaster is not None):
            if freq == FREQ_YEARLY:
                bymonth = dtstart.month
                bymonthday = dtstart.day
            elif freq == FREQ_MONTHLY:
                bymonthday = dtstart.day
            elif freq == FREQ_WEEKLY:
                byweekday = dtstart.weekday()
        # bymonth
        if not bymonth:
            self._bymonth = None
        elif type(bymonth) is int:
            self._bymonth = (bymonth,)
        else:
            self._bymonth = tuple(bymonth)
        # byyearday
        if not byyearday:
            self._byyearday = None
        elif type(byyearday) is int:
            self._byyearday = (byyearday,)
        else:
            self._byyearday = tuple(byyearday)
        # byeaster
        if byeaster is not None:
            if not easter:
                from dateutil import easter
            if type(byeaster) is int:
                self._byeaster = (byeaster,)
            else:
                self._byeaster = tuple(byeaster)
        else:
            self._byeaster = None
        # bymonthay
        if not bymonthday:
            self._bymonthday = None
        elif type(bymonthday) is int:
            self._bymonthday = (bymonthday,)
        else:
            self._bymonthday = tuple(bymonthday)
        # byweekno
        if byweekno is None:
            self._byweekno = None
        elif type(byweekno) is int:
            self._byweekno = (byweekno,)
        else:
            self._byweekno = tuple(byweekno)
        # byweekday / bynweekday
        if byweekday is None:
            self._byweekday = None
            self._bynweekday = None
        elif type(byweekday) is int:
            self._byweekday = (byweekday,)
            self._bynweekday = None
        elif hasattr(byweekday, "n"):
            if byweekday.n == 0:
                self._byweekday = (byweekday.weekday,)
                self._bynweekday = None
            else:
                self._bynweekday = ((byweekday.weekday, byweekday.n),)
                self._byweekday = None
        else:
            self._byweekday = []
            self._bynweekday = []
            for wday in byweekday:
                if type(wday) is int:
                    self._byweekday.append(weekday)
                elif wday.n == 0:
                    self._byweekday.append(wday.weekday)
                else:
                    self._bynweekday.append((wday.weekday, wday.n))
            self._byweekday = tuple(self._byweekday)
            self._bynweekday = tuple(self._bynweekday)
            if not self._byweekday:
                self._byweekday = None
            elif not self._bynweekday:
                self._bynweekday = None
        # byhour
        if byhour is None:
            if freq < FREQ_HOURLY:
                self._byhour = (dtstart.hour,)
            else:
                self._byhour = None
        elif type(byhour) is int:
            self._byhour = (byhour,)
        else:
            self._byhour = tuple(byhour)
        # byminute
        if byminute is None:
            if freq < FREQ_MINUTELY:
                self._byminute = (dtstart.minute,)
            else:
                self._byminute = None
        elif type(byminute) is int:
            self._byminute = (byminute,)
        else:
            self._byminute = tuple(byminute)
        # bysecond
        if bysecond is None:
            if freq < FREQ_SECONDLY:
                self._bysecond = (dtstart.second,)
            else:
                self._bysecond = None
        elif type(bysecond) is int:
            self._bysecond = (bysecond,)
        else:
            self._bysecond = tuple(bysecond)

        if self._freq >= FREQ_HOURLY:
            self._timeset = None
        else:
            self._timeset = []
            for hour in self._byhour:
                for minute in self._byminute:
                    for second in self._bysecond:
                        self._timeset.append(
                                datetime.time(hour, minute, second,
                                                    tzinfo=self._tzinfo))
            self._timeset.sort()
            self._timeset = tuple(self._timeset)

    def iter(self, dtstart):
        year, month, day, hour, minute, second, weekday, yearday, _ = \
            dtstart.timetuple()

        freq = self._freq

        ii = _iterinfo(self)
        ii.rebuild(year, month)

        getdayset = {FREQ_YEARLY:ii.ydayset,
                     FREQ_MONTHLY:ii.mdayset,
                     FREQ_WEEKLY:ii.wdayset,
                     FREQ_DAILY:ii.ddayset,
                     FREQ_HOURLY:ii.ddayset,
                     FREQ_MINUTELY:ii.ddayset,
                     FREQ_SECONDLY:ii.ddayset}[freq]
        
        count = self._count

        if freq < FREQ_HOURLY:
            timeset = self._timeset
        else:
            gettimeset = {FREQ_HOURLY:ii.htimeset,
                          FREQ_MINUTELY:ii.mtimeset,
                          FREQ_SECONDLY:ii.stimeset}[freq]
            if ((freq >= FREQ_HOURLY and
                 self._byhour and hour not in self._byhour) or
                (freq >= FREQ_MINUTELY and
                 self._byminute and minute not in self._byminute) or
                (freq >= FREQ_MINUTELY and
                 self._bysecond and minute not in self._bysecond)):
                timeset = ()
            else:
                timeset = gettimeset(hour, minute, second)

        while True:
            # Get dayset with the right frequency
            dayset, start, end = getdayset(year, month, day)

            # Do the "hard" work ;-)
            for i in dayset[start:end]:
                if ((self._bymonth and ii.mmask[i] not in self._bymonth) or
                    (self._byweekno and not ii.wnomask[i]) or
                    (self._byyearday and i+1 not in self._byyearday) or
                    (self._bymonthday and
                        ii.mdaymask[i] not in self._bymonthday) or
                    (self._byweekday and
                        ii.wdaymask[i] not in self._byweekday) or
                    (ii.nwdaymask and not ii.nwdaymask[i]) or
                    (self._byeaster and not ii.eastermask[i])):
                    dayset[i] = None

            # Output results
            if self._bysetpos and self._timeset:
                for pos in self._bysetpos:
                    if pos < 0:
                        daypos, timepos = divmod(pos, len(self._timeset))
                    else:
                        daypos, timepos = divmod(pos-1, len(self._timeset))
                    try:
                        i = [x for x in dayset[start:end]
                                if x is not None][daypos]
                        time = timeset[timepos]
                    except IndexError:
                        pass
                    else:
                        date = datetime.date.fromordinal(ii.yearordinal+i)
                        res = datetime.datetime.combine(date, time)
                        if self._until and res > until:
                            return
                        elif res >= dtstart:
                            yield res
                            if count:
                                count -= 1
                                if not count:
                                    return
            else:
                for i in dayset[start:end]:
                    if i is not None:
                        date = datetime.date.fromordinal(ii.yearordinal+i)
                        for time in timeset:
                            res = datetime.datetime.combine(date, time)
                            if self._until and res > self._until:
                                return
                            elif res >= dtstart:
                                yield res
                                if count:
                                    count -= 1
                                    if not count:
                                        return

            # Handle frequency and interval
            fixday = False
            if freq == FREQ_YEARLY:
                year += self._interval
                ii.rebuild(year, month)
            elif freq == FREQ_MONTHLY:
                month += self._interval
                if month > 12:
                    div, mod = divmod(month, 12)
                    month = mod
                    year += div
                    if month == 0:
                        month = 12
                        year -= 1
                ii.rebuild(year, month)
            elif freq == FREQ_WEEKLY:
                if self._wkst > weekday:
                    day += -(weekday+1+(6-self._wkst))+self._interval*7
                else:
                    day += -(weekday-self._wkst)+self._interval*7
                weekday = self._wkst
                fixday = True
            elif freq == FREQ_DAILY:
                day += self._interval
                fixday = True
            elif freq == FREQ_HOURLY:
                while True:
                    hour += self._interval
                    div, mod = divmod(hour, 24)
                    if div:
                        hour = mod
                        day += div
                        fixday = True
                    if not self._byhour or hour in self._byhour:
                        break
                timeset = gettimeset(hour, minute, second)
            elif freq == FREQ_MINUTELY:
                while True:
                    minute += self._interval
                    div, mod = divmod(minute, 60)
                    if div:
                        minute = mod
                        hour += div
                        div, mod = divmod(hour, 24)
                        if div:
                            hour = mod
                            day += div
                            fixday = True
                    if ((not self._byhour or hour in self._byhour) and
                        (not self._byminute or minute in self._byminute)):
                        break
                timeset = gettimeset(hour, minute, second)
            elif freq == FREQ_SECONDLY:
                while True:
                    second += self._interval
                    div, mod = divmod(second, 60)
                    if div:
                        second = mod
                        minute += div
                        div, mod = divmod(minute, 60)
                        if div:
                            minute = mod
                            hour += div
                            div, mod = divmod(hour, 24)
                            if div:
                                hour = mod
                                day += div
                                fixday = True
                    if ((not self._byhour or hour in self._byhour) and
                        (not self._byminute or minute in self._byminute) and
                        (not self._bysecond or second in self._bysecond)):
                        break
                timeset = gettimeset(hour, minute, second)

            if fixday and day > 28:
                daysinmonth = calendar.monthrange(year, month)[1]
                if day > daysinmonth:
                    while day > daysinmonth:
                        day -= daysinmonth
                        month += 1
                        if month == 13:
                            month = 1
                            year += 1
                        daysinmonth = calendar.monthrange(year, month)[1]
                    ii.rebuild(year, month)

    def __iter__(self):
        return self.iter(self._dtstart)
            
    def before(self, dt, inc=False):
        last = None
        if inc:
            for i in self:
                if i > dt:
                    break
                last = i
        else:
            for i in self:
                if i >= dt:
                    break
                last = i
        return last

    def after(self, dt, inc=False):
        if inc:
            for i in self:
                if i >= dt:
                    return i
        else:
            for i in self:
                if i > dt:
                    return i
        return None

class _iterinfo(object):
    __slots__ = ["rrule", "yearlen", "yearordinal", "lastyear", "lastmonth",
                 "mmask", "mrange", "mdaymask",
                 "wdaymask", "wnomask", "nwdaymask",
                 "eastermask"]

    def __init__(self, rrule):
        for attr in self.__slots__:
            setattr(self, attr, None)
        self.rrule = rrule

    def rebuild(self, year, month):
        rr = self.rrule
        if year != self.lastyear:
            self.yearlen = 365+calendar.isleap(year)
            self.yearordinal = datetime.date(year,1,1).toordinal()

            wday = datetime.date(year, 1, 1).weekday()
            if self.yearlen == 365:
                self.mmask = M365MASK
                self.mdaymask = MDAY365MASK
                self.wdaymask = WDAYMASK[wday:wday+365]
                self.mrange = M365RANGE
            else:
                self.mmask = M366MASK
                self.mdaymask = MDAY366MASK
                self.wdaymask = WDAYMASK[wday:wday+366]
                self.mrange = M366RANGE

            if not rr._byweekno:
                self.wnomask = None
            else:
                self.wnomask = [0]*self.yearlen
                no1wkst = firstwkst = self.wdaymask.find(rr._wkst)
                if no1wkst+1 > 4:
                    no1wkst = 0
                numweeks = 52+(self.yearlen-no1wkst)%7/4
                for n in rr._byweekno:
                    if n < 0:
                        n += numweeks+1
                    if n > 1:
                        i = no1wkst+(n-1)*7
                        while self.wdaymask[i] != rr._wkst:
                            i -= 1
                    else:
                        i = 0
                    for j in range(7):
                        self.wnomask[i] = 1
                        i += 1
                        if self.wdaymask[i] == rr._wkst or i == self.yearlen:
                            break

        if (rr._bynweekday and
            (month != self.lastmonth or year != self.lastyear)):
            ranges = []
            if rr._freq == FREQ_YEARLY:
                if rr._bymonth:
                    for month in rr._bymonth:
                        ranges.append(self.mrange[month-1:month+1])
                else:
                    ranges = [(0, self.yearlen)]
            elif rr._freq == FREQ_MONTHLY:
                ranges = [self.mrange[month-1:month+1]]
            if ranges:
                self.nwdaymask = [0]*self.yearlen
                for first, last in ranges:
                    last -= 1
                    for wday, n in rr._bynweekday:
                        if n < 0:
                            i = last
                            s = -1
                        else:
                            i = first
                            s = 1
                        while self.wdaymask[i] != wday:
                            i += s
                        i += (n-s)*7*s
                        if first <= i <= last:
                            self.nwdaymask[i] = 1

        if rr._byeaster:
            self.eastermask = [0]*self.yearlen
            eyday = easter.easter(year).toordinal()-self.yearordinal
            for offset in rr._byeaster:
                self.eastermask[eyday+offset] = 1

        self.lastyear = year
        self.lastmonth = month

    def ydayset(self, year, month, day):
        return range(self.yearlen), 0, self.yearlen

    def mdayset(self, year, month, day):
        set = [None]*self.yearlen
        start, end = self.mrange[month-1:month+1]
        for i in range(start, end):
            set[i] = i
        return set, start, end

    def wdayset(self, year, month, day):
        set = [None]*self.yearlen
        i = datetime.date(year, month, day).toordinal()-self.yearordinal
        start = i
        for j in range(7):
            set[i] = i
            i += 1
            if (not (0 <= i < self.yearlen) or
                self.wdaymask[i] == self.rrule._wkst):
                break
        return set, start, i

    def ddayset(self, year, month, day):
        set = [None]*self.yearlen
        i = datetime.date(year, month, day).toordinal()-self.yearordinal
        set[i] = i
        return set, i, i+1

    def htimeset(self, hour, minute, second):
        set = []
        rr = self.rrule
        for minute in rr._byminute:
            for second in rr._bysecond:
                set.append(datetime.time(hour, minute, second,
                                                    tzinfo=rr._tzinfo))
        set.sort()
        return set

    def mtimeset(self, hour, minute, second):
        set = []
        rr = self.rrule
        for second in rr._bysecond:
            set.append(datetime.time(hour, minute, second, tzinfo=rr._tzinfo))
        set.sort()
        return set

    def stimeset(self, hour, minute, second):
        return (datetime.time(hour, minute, second, self.rrule._tzinfo),)


class rruleset:

    class _genitem:
        def __init__(self, genlist, gen):
            try:
                self.dt = gen()
                genlist.append(self)
            except StopIteration:
                pass
            self.genlist = genlist
            self.gen = gen

        def next(self):
            try:
                self.dt = self.gen()
            except StopIteration:
                self.genlist.remove(self)

        def __cmp__(self, other):
            return cmp(self.dt, other.dt)

    def __init__(self):
        self._rrule = []
        self._rdate = []
        self._exrule = []
        self._exdate = []

    def append_rrule(self, rrule):
        self._rrule.append(rrule)
    
    def remove_rrule(self, rrule):
        self._rrule.remove(rrule)

    def append_rdate(self, rdate):
        self._rdate.append(rdate)

    def remove_rdate(self, rdate):
        self._rdate.remove(rdate)

    def append_exrule(self, exrule):
        self._exrule.append(exrule)
    
    def remove_exrule(self, exrule):
        self._exrule.remove(exrule)

    def append_exdate(self, exdate):
        self._exdate.append(exdate)

    def remove_exdate(self, exdate):
        self._exdate.remove(exdate)

    def __iter__(self):
        rlist = []
        self._genitem(rlist, iter(self._rdate).next)
        for gen in [iter(x).next for x in self._rrule]:
            self._genitem(rlist, gen)
        rlist.sort()
        exlist = []
        self._genitem(exlist, iter(self._exdate).next)
        for gen in [iter(x).next for x in self._exrule]:
            self._genitem(exlist, gen)
        exlist.sort()
        lastdt = None
        while rlist:
            ritem = rlist[0]
            if not lastdt or lastdt != ritem.dt:
                while exlist and exlist[0] < ritem:
                    exlist[0].next()
                    exlist.sort()
                if not exlist or ritem != exlist[0]:
                    yield ritem.dt
                lastdt = ritem.dt
            ritem.next()
            rlist.sort()

    def before(self, dt, inc=False):
        last = None
        if inc:
            for i in self:
                if i > dt:
                    break
                last = i
        else:
            for i in self:
                if i >= dt:
                    break
                last = i
        return last

    def after(self, dt, inc=False):
        if inc:
            for i in self:
                if i >= dt:
                    return i
        else:
            for i in self:
                if i > dt:
                    return i
        return None

class _rrulestr:

    _freq_map = {"YEARLY": FREQ_YEARLY,
                 "MONTHLY": FREQ_MONTHLY,
                 "WEEKLY": FREQ_WEEKLY,
                 "DAILY": FREQ_DAILY,
                 "HOURLY": FREQ_HOURLY,
                 "MINUTELY": FREQ_MINUTELY,
                 "SECONDLY": FREQ_SECONDLY}

    _weekday_map = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}

    def _handle_int(self, kwargs, name, value):
        kwargs[name.lower()] = int(value)

    def _handle_int_list(self, kwargs, name, value):
        kwargs[name.lower()] = [int(x) for x in value.split(',')]

    _handle_INTERVAL   = _handle_int
    _handle_COUNT      = _handle_int
    _handle_BYSETPOS   = _handle_int_list
    _handle_BYMONTH    = _handle_int_list
    _handle_BYMONTHDAY = _handle_int_list
    _handle_BYYEARDAY  = _handle_int_list
    _handle_BYEASTER   = _handle_int_list
    _handle_BYWEEKNO   = _handle_int_list
    _handle_BYHOUR     = _handle_int_list
    _handle_BYMINUTE   = _handle_int_list
    _handle_BYSECOND   = _handle_int_list

    def _handle_FREQ(self, kwargs, name, value):
        kwargs["freq"] = self._freq_map[value]

    def _handle_UNTIL(self, kwargs, name, value):
        global parser
        if not parser:
            from dateutil import parser
        try:
            kwargs["until"] = parser.parse(value)
        except ValueError:
            raise ValueError, "invalid until date"

    def _handle_WKST(self, kwargs, name, value):
        kwargs["wkst"] = self._weekday_map[value]

    def _handle_BYWEEKDAY(self, kwargs, name, value):
        l = []
        for wday in value.split(','):
            for i in range(len(wday)):
                if wday[i] not in '+-0123456789':
                    break
            n = wday[:i] or 0
            w = wday[i:]
            if n: n = int(n)
            l.append(weekdays[self._weekday_map[w]](n))
        kwargs["byweekday"] = l

    _handle_BYDAY = _handle_BYWEEKDAY

    def _parse_rfc_rrule(self, line, dtstart=None):
        if line.find(':') != -1:
            name, value = line.split(':')
            if name != "RRULE":
                raise ValueError, "unknown parameter name"
        else:
            value = line
        kwargs = {}
        for pair in value.split(';'):
            name, value = pair.split('=')
            name = name.upper()
            value = value.upper()
            try:
                getattr(self, "_handle_"+name)(kwargs, name, value)
            except AttributeError:
                raise "unknown parameter '%s'" % name
            except (KeyError, ValueError):
                raise "invalid '%s': %s" % (name, value)
        return rrule(dtstart=dtstart, **kwargs)

    def _parse_rfc(self, s,
                   dtstart=None,
                   unfold=False,
                   forceset=False,
                   compatible=False,
                   ignoretz=False):
        global parser
        if compatible:
            forceset = True
        s = s.upper()
        lines = s.splitlines()
        if not lines:
            raise ValueError, "empty string"
        if unfold:
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()
                if not line:
                    del lines[i]
                elif i > 0 and line[0] == " ":
                    lines[i-1] += line[1:]
                    del lines[i]
                else:
                    i += 1
        else:
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    del lines[i]
                else:
                    lines[i] = line
                    i += 1
        if (not forceset and
              len(lines) == 1 and (not s.find(':') or s.startswith('RRULE:'))):
            return self._parse_rfc_rrule(s)
        else:
            rrulevals = []
            rdatevals = []
            exrulevals = []
            exdatevals = []
            for line in lines:
                if not line:
                    continue
                name, value = line.split(':', 1)
                parms = name.split(';')
                if not parms:
                    raise ValueError, "empty property name"
                name = parms[0]
                parms = parms[1:]
                if name == "RRULE":
                    for parm in parms:
                        raise ValueError, "unsupported RRULE parm: "+parm
                    rrulevals.append(value)
                elif name == "RDATE":
                    for parm in parms:
                        if parm != "VALUE=DATE-TIME":
                            raise ValueError, "unsupported RDATE parm: "+parm
                    rdatevals.append(value)
                elif name == "EXRULE":
                    for parm in parms:
                        raise ValueError, "unsupported EXRULE parm: "+parm
                    exrulevals.append(value)
                elif name == "EXDATE":
                    for parm in parms:
                        if parm != "VALUE=DATE-TIME":
                            raise ValueError, "unsupported RDATE parm: "+parm
                    exdatevals.append(value)
                elif name == "DTSTART":
                    for parm in parms:
                        raise ValueError, "unsupported DTSTART parm: "+parm
                    if not parser:
                        from dateutil import parser
                    dtstart = parser.parse(value, ignoretz=ignoretz)
                else:
                    raise ValueError, "unsupported property: "+name
            if (forceset or len(rrulevals) > 1 or
                rdatevals or exrulevals or exdatevals):
                if not parser and (rdatevals or exdatevals):
                    from dateutil import parser
                set = rruleset()
                for value in rrulevals:
                    set.append_rrule(self._parse_rfc_rrule(value,
                                                           dtstart=dtstart))
                for value in rdatevals:
                    for datestr in value.split(','):
                        set.append_rdate(parser.parse(datestr,
                                                      ignoretz=ignoretz))
                for value in exrulevals:
                    set.append_exrule(self._parse_rfc_rrule(value,
                                                            dtstart=dtstart))
                for value in exdatevals:
                    for datestr in value.split(','):
                        set.append_exdate(parser.parse(datestr,
                                                       ignoretz=ignoretz))
                if compatible and dtstart:
                    set.append_rdate(dtstart)
                return set
            else:
                return self._parse_rfc_rrule(rrulevals[0], dtstart=dtstart)

    def __call__(self, s, **kwargs):
        return self._parse_rfc(s, **kwargs)

rrulestr = _rrulestr()

# vim:ts=4:sw=4:et
