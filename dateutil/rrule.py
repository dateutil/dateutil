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

class weekday(object):
    __slots__ = ["weekday", "n"]

    def __init__(self, weekday, n=0):
        self.weekday = weekday
        self.n = n

    def __call__(self, n):
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
    def __init__(self, dtstart, freq,
                 interval=1, wkst=0, count=None, until=None, bysetpos=None,
                 bymonth=None, bymonthday=None, byyearday=None,
                 byweekno=None, byweekday=None,
                 byhour=None, byminute=None, bysecond=None):
        self._dtstart = dtstart
        self._freq = freq
        self._interval = interval
        self._count = count
        self._until = until
        self._bysetpos = bysetpos
        if type(wkst) is int:
            self._wkst = wkst
        else:
            self._wkst = wkst.weekday
        if not (bymonth or byweekno or byyearday or
                bymonthday or byweekday is not None):
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
                                datetime.time(hour, minute, second))
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
                    (ii.nwdaymask and not ii.nwdaymask[i])):
                    dayset[i] = None

            # Output results
            if self._bysetpos and self._timeset:
                if self._bysetpos < 0:
                    daypos, timepos = divmod(self._bysetpos,
                                             len(self._timeset))
                else:
                    daypos, timepos = divmod(self._bysetpos-1,
                                             len(self._timeset))
                try:
                    #print [datetime.date.fromordinal(ii.yearordinal+x)
                    #       for x in set[start:end] if x is not None]
                    i = [x for x in dayset[start:end] if x is not None][daypos]
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
                            if self._until and res > until:
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

class _iterinfo(object):
    __slots__ = ["rrule", "yearlen", "yearordinal", "lastyear", "lastmonth",
                 "mmask", "mrange", "mdaymask",
                 "wdaymask", "wnomask", "nwdaymask"]

    def __init__(self, rrule):
        for attr in self.__slots__:
            setattr(self, attr, None)
        self.rrule = rrule

    def rebuild(self, year, month):
        rr = self.rrule
        if year != self.lastyear:
            self.lastyear = year
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

        if rr._bynweekday and month != self.lastmonth:
            self.lastmonth = month
            ranges = []
            if rr._freq == YEARLY:
                if rr._bymonth:
                    for month in rr._bymonth:
                        ranges.append(self.mrange[month-1:month+1])
                else:
                    ranges = [(0, self.yearlen)]
            elif rr._freq == MONTHLY:
                ranges = [self.mrange[month-1:month+1]]
            if ranges:
                self.nwdaymask = [0]*self.yearlen
                for first, last in ranges:
                    last -= 1
                    for wday, n in rr._bynweekday:
                        s = n/abs(n)
                        if n < 0:
                            i = last
                            s = -1
                        else:
                            i = first
                            s = 1
                        while self.wdaymask[i] != wday:
                            i += s
                        i += (n-1)*7*s
                        if first <= i <= last:
                            self.nwdaymask[i] = 1

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
        for minute in self.rrule._byminute:
            for second in self.rrule._bysecond:
                set.append(datetime.time(hour, minute, second))
        set.sort()
        return set

    def mtimeset(self, hour, minute, second):
        set = []
        for second in self.rrule._bysecond:
            set.append(datetime.time(hour, minute, second))
        set.sort()
        return set

    def stimeset(self, hour, minute, second):
        return (datetime.time(hour, minute, second),)

# vim:ts=4:sw=4:et
