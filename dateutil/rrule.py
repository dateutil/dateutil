import datetime
import calendar
import thread

__all__ = ["rrule", "rruleset", "rrulestr",
           "FREQ_YEARLY", "FREQ_MONTHLY", "FREQ_WEEKLY", "FREQ_DAILY",
           "FREQ_HOURLY", "FREQ_MINUTELY", "FREQ_SECONDLY",
           "MO", "TU", "WE", "TH", "FR", "SA", "SU"]

M366MASK = tuple([1]*31+[2]*29+[3]*31+[4]*30+[5]*31+[6]*30+
                 [7]*31+[8]*31+[9]*30+[10]*31+[11]*30+[12]*31)
M365MASK = list(M366MASK)
M29, M30, M31 = range(1,30), range(1,31), range(1,32)
MDAY366MASK = tuple(M31+M29+M31+M30+M31+M30+M31+M31+M30+M31+M30+M31)
MDAY365MASK = list(MDAY366MASK)
M29, M30, M31 = range(-29,0), range(-30,0), range(-31,0)
NMDAY366MASK = tuple(M31+M29+M31+M30+M31+M30+M31+M31+M30+M31+M30+M31)
NMDAY365MASK = list(NMDAY366MASK)
M366RANGE = (0,31,60,91,121,152,182,213,244,274,305,335,366)
M365RANGE = (0,31,59,90,120,151,181,212,243,273,304,334,365)
WDAYMASK = [0,1,2,3,4,5,6]*54
del M29, M30, M31, M365MASK[59], MDAY365MASK[59], NMDAY365MASK[31]
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
                 byhour=None, byminute=None, bysecond=None,
                 cache=False):
        if cache:
            self._cache = []
            self._cache_lock = thread.allocate_lock()
            self._cache_gen  = self._iter()
        else:
            self._cache = None
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
        if not (byweekno or byyearday or bymonthday or
                byweekday is not None or byeaster is not None):
            if freq == FREQ_YEARLY:
                if not bymonth:
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
            self._bymonthday = ()
            self._bynmonthday = ()
        elif type(bymonthday) is int:
            if bymonthday < 0:
                self._bynmonthday = (bymonthday,)
                self._bymonthday = ()
            else:
                self._bymonthday = (bymonthday,)
                self._bynmonthday = ()
        else:
            self._bymonthday = tuple([x for x in bymonthday if x > 0])
            self._bynmonthday = tuple([x for x in bymonthday if x < 0])
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
                    self._byweekday.append(wday)
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

        #self._compile_pred()
    
    def _compile_pred(self):
        predlist = []
        if self._byweekday:
            predlist.append("(ii.wdaymask[i] not in self._byweekday)")
        if self._bymonth:
            predlist.append("(ii.mmask[i] not in self._bymonth)")
        if self._bymonthday and self._bynmonthday:
            predlist.append("(ii.mdaymask[i] not in self._bymonthday and"
                            " ii.nmdaymask[i] not in self._bynmonthday)")
        elif self._bymonthday:
            predlist.append("(ii.mdaymask[i] not in self._bymonthday)")
        elif self._bynmonthday:
            predlist.append("(ii.nmdaymask[i] not in self._bynmonthday)")
        if self._byweekno:
            predlist.append("(not ii.wnomask[i])")
        if self._byyearday:
            predlist.append("(i+1 not in self._byyearday)")
        if self._bynweekday and self._freq in (FREQ_YEARLY, FREQ_MONTHLY):
            predlist.append("(not ii.nwdaymask[i])")
        if self._byeaster:
            predlist.append("(ii.eastermask[i])")
        if predlist:
            self._pred = compile(" or ".join(predlist), "<string>", "eval")
        else:
            self._pred = compile("False", "<string>", "eval")

    def _iter_cached(self):
        i = 0
        while True:
            if i == len(self._cache):
                self._cache_lock.acquire()
                try:
                    try:
                        for j in range(10):
                            self._cache.append(self._cache_gen.next())
                    except StopIteration:
                        self._cache.append(None)
                finally:
                    self._cache_lock.release()
            item = self._cache[i]
            if item is None:
                return
            else:
                yield item
            i += 1

    def _iter(self):
        year, month, day, hour, minute, second, weekday, yearday, _ = \
            self._dtstart.timetuple()

        # Some local variables to speed things up a bit
        freq = self._freq
        interval = self._interval
        wkst = self._wkst
        until = self._until
        bymonth = self._bymonth
        byweekno = self._byweekno
        byyearday = self._byyearday
        byweekday = self._byweekday
        byeaster = self._byeaster
        bymonthday = self._bymonthday
        bynmonthday = self._bynmonthday
        bysetpos = self._bysetpos
        byhour = self._byhour
        byminute = self._byminute
        bysecond = self._bysecond

        ii = _iterinfo(self)
        ii.rebuild(year, month)

        getdayset = {FREQ_YEARLY:ii.ydayset,
                     FREQ_MONTHLY:ii.mdayset,
                     FREQ_WEEKLY:ii.wdayset,
                     FREQ_DAILY:ii.ddayset,
                     FREQ_HOURLY:ii.ddayset,
                     FREQ_MINUTELY:ii.ddayset,
                     FREQ_SECONDLY:ii.ddayset}[freq]
        
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

        count = self._count
        while True:
            # Get dayset with the right frequency
            dayset, start, end = getdayset(year, month, day)

            # Do the "hard" work ;-)
            filtered = False
            for i in dayset[start:end]:
                #if eval(self._pred):
                if ((bymonth and ii.mmask[i] not in bymonth) or
                    (byweekno and not ii.wnomask[i]) or
                    (byyearday and i+1 not in byyearday) or
                    (byweekday and ii.wdaymask[i] not in byweekday) or
                    (ii.nwdaymask and not ii.nwdaymask[i]) or
                    (byeaster and not ii.eastermask[i]) or
                    ((bymonthday or bynmonthday) and
                     ii.mdaymask[i] not in bymonthday and
                     ii.nmdaymask[i] not in bynmonthday)):
                    dayset[i] = None
                    filtered = True

            # Output results
            if bysetpos and timeset:
                for pos in bysetpos:
                    if pos < 0:
                        daypos, timepos = divmod(pos, len(timeset))
                    else:
                        daypos, timepos = divmod(pos-1, len(timeset))
                    try:
                        i = [x for x in dayset[start:end]
                                if x is not None][daypos]
                        time = timeset[timepos]
                    except IndexError:
                        pass
                    else:
                        date = datetime.date.fromordinal(ii.yearordinal+i)
                        res = datetime.datetime.combine(date, time)
                        if until and res > until:
                            return
                        elif res >= self._dtstart:
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
                            if until and res > until:
                                return
                            elif res >= self._dtstart:
                                yield res
                                if count:
                                    count -= 1
                                    if not count:
                                        return

            # Handle frequency and interval
            fixday = False
            if freq == FREQ_YEARLY:
                year += interval
                ii.rebuild(year, month)
            elif freq == FREQ_MONTHLY:
                month += interval
                if month > 12:
                    div, mod = divmod(month, 12)
                    month = mod
                    year += div
                    if month == 0:
                        month = 12
                        year -= 1
                ii.rebuild(year, month)
            elif freq == FREQ_WEEKLY:
                if wkst > weekday:
                    day += -(weekday+1+(6-wkst))+self._interval*7
                else:
                    day += -(weekday-wkst)+self._interval*7
                weekday = wkst
                fixday = True
            elif freq == FREQ_DAILY:
                day += interval
                fixday = True
            elif freq == FREQ_HOURLY:
                if filtered:
                    # Jump to one iteration before next day
                    hour += ((23-hour)//interval)*interval
                while True:
                    hour += interval
                    div, mod = divmod(hour, 24)
                    if div:
                        hour = mod
                        day += div
                        fixday = True
                    if not byhour or hour in byhour:
                        break
                timeset = gettimeset(hour, minute, second)
            elif freq == FREQ_MINUTELY:
                if filtered:
                    # Jump to one iteration before next day
                    minute += ((1439-(hour*60+minute))//interval)*interval
                while True:
                    minute += interval
                    div, mod = divmod(minute, 60)
                    if div:
                        minute = mod
                        hour += div
                        div, mod = divmod(hour, 24)
                        if div:
                            hour = mod
                            day += div
                            fixday = True
                            filtered = False
                    if ((not byhour or hour in byhour) and
                        (not byminute or minute in byminute)):
                        break
                timeset = gettimeset(hour, minute, second)
            elif freq == FREQ_SECONDLY:
                if filtered:
                    # Jump to one iteration before next day
                    second += (((86399-(hour*3600+minute*60+second))
                                //interval)*interval)
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
                    if ((not byhour or hour in byhour) and
                        (not byminute or minute in byminute) and
                        (not bysecond or second in bysecond)):
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
        if self._cache is None:
            return self._iter()
        else:
            return self._iter_cached()
            
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

    def between(self, after, before, inc=False):
        started = False
        l = []
        if inc:
            for i in self:
                if not started:
                    if i >= after:
                        started = True
                        l.append(i)
                else:
                    if i > before:
                        break
                    l.append(i)
        else:
            for i in self:
                if not started:
                    if i > after:
                        started = True
                        l.append(i)
                else:
                    if i >= before:
                        break
                    l.append(i)
        return l

class _iterinfo(object):
    __slots__ = ["rrule", "yearlen", "yearordinal", "lastyear", "lastmonth",
                 "mmask", "mrange", "mdaymask", "nmdaymask",
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
                self.nmdaymask = NMDAY365MASK
                self.wdaymask = WDAYMASK[wday:wday+365]
                self.mrange = M365RANGE
            else:
                self.mmask = M366MASK
                self.mdaymask = MDAY366MASK
                self.nmdaymask = NMDAY366MASK
                self.wdaymask = WDAYMASK[wday:wday+366]
                self.mrange = M366RANGE

            if not rr._byweekno:
                self.wnomask = None
            else:
                self.wnomask = [0]*self.yearlen
                no1wkst = firstwkst = self.wdaymask.index(rr._wkst)
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
                        i += (n-s)*7
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
        # We need to handle cross-year weeks here.
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
        return (datetime.time(hour, minute, second,
                tzinfo=self.rrule._tzinfo),)


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

    def __init__(self, cache=False):
        self._rrule = []
        self._rdate = []
        self._exrule = []
        self._exdate = []

        if cache:
            self._cache = []
            self._cache_lock = thread.allocate_lock()
            self._cache_gen  = self._iter()
        else:
            self._cache = None

    def rrule(self, rrule):
        self._rrule.append(rrule)
    
    def rdate(self, rdate):
        self._rdate.append(rdate)

    def exrule(self, exrule):
        self._exrule.append(exrule)

    def exdate(self, exdate):
        self._exdate.append(exdate)

    def _iter_cached(self):
        i = 0
        while True:
            if i == len(self._cache):
                self._cache_lock.acquire()
                try:
                    try:
                        for i in range(10):
                            self._cache.append(self._cache_gen.next())
                    except StopIteration:
                        self._cache.append(None)
                finally:
                    self._cache_lock.release()
            item = self._cache[i]
            if item is None:
                return
            else:
                yield item
            i += 1

    def _iter(self):
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

    def __iter__(self):
        if self._cache is None:
            return self._iter()
        else:
            return self._iter_cached()

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

    def between(self, after, before, inc=False):
        started = False
        l = []
        if inc:
            for i in self:
                if not started:
                    if i >= after:
                        started = True
                        l.append(i)
                else:
                    if i > before:
                        break
                    l.append(i)
        else:
            for i in self:
                if not started:
                    if i > after:
                        started = True
                        l.append(i)
                else:
                    if i >= before:
                        break
                    l.append(i)
        return l


class _rrulestr:

    _freq_map = {"YEARLY": FREQ_YEARLY,
                 "MONTHLY": FREQ_MONTHLY,
                 "WEEKLY": FREQ_WEEKLY,
                 "DAILY": FREQ_DAILY,
                 "HOURLY": FREQ_HOURLY,
                 "MINUTELY": FREQ_MINUTELY,
                 "SECONDLY": FREQ_SECONDLY}

    _weekday_map = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}

    def _handle_int(self, rrkwargs, name, value, **kwargs):
        rrkwargs[name.lower()] = int(value)

    def _handle_int_list(self, rrkwargs, name, value, **kwargs):
        rrkwargs[name.lower()] = [int(x) for x in value.split(',')]

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

    def _handle_FREQ(self, rrkwargs, name, value, **kwargs):
        rrkwargs["freq"] = self._freq_map[value]

    def _handle_UNTIL(self, rrkwargs, name, value, **kwargs):
        global parser
        if not parser:
            from dateutil import parser
        try:
            rrkwargs["until"] = parser.parse(value,
                                           ignoretz=kwargs.get("ignoretz"),
                                           tzinfos=kwargs.get("tzinfos"))
        except ValueError:
            raise ValueError, "invalid until date"

    def _handle_WKST(self, rrkwargs, name, value, **kwargs):
        rrkwargs["wkst"] = self._weekday_map[value]

    def _handle_BYWEEKDAY(self, rrkwargs, name, value, **kwarsg):
        l = []
        for wday in value.split(','):
            for i in range(len(wday)):
                if wday[i] not in '+-0123456789':
                    break
            n = wday[:i] or 0
            w = wday[i:]
            if n: n = int(n)
            l.append(weekdays[self._weekday_map[w]](n))
        rrkwargs["byweekday"] = l

    _handle_BYDAY = _handle_BYWEEKDAY

    def _parse_rfc_rrule(self, line,
                         dtstart=None,
                         cache=False,
                         ignoretz=False,
                         tzinfos=None):
        if line.find(':') != -1:
            name, value = line.split(':')
            if name != "RRULE":
                raise ValueError, "unknown parameter name"
        else:
            value = line
        rrkwargs = {}
        for pair in value.split(';'):
            name, value = pair.split('=')
            name = name.upper()
            value = value.upper()
            try:
                getattr(self, "_handle_"+name)(rrkwargs, name, value,
                                               ignoretz=ignoretz,
                                               tzinfos=tzinfos)
            except AttributeError:
                raise "unknown parameter '%s'" % name
            except (KeyError, ValueError):
                raise "invalid '%s': %s" % (name, value)
        return rrule(dtstart=dtstart, cache=cache, **rrkwargs)

    def _parse_rfc(self, s,
                   dtstart=None,
                   cache=False,
                   unfold=False,
                   forceset=False,
                   compatible=False,
                   ignoretz=False,
                   tzinfos=None):
        global parser
        if compatible:
            forceset = True
            unfold = True
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
        if (not forceset and len(lines) == 1 and
            (s.find(':') == -1 or s.startswith('RRULE:'))):
            return self._parse_rfc_rrule(s, cache=cache, dtstart=dtstart,
                                         ignoretz=ignoretz, tzinfos=tzinfos)
        else:
            rrulevals = []
            rdatevals = []
            exrulevals = []
            exdatevals = []
            for line in lines:
                if not line:
                    continue
                if line.find(':') == -1:
                    name = "RRULE"
                    value = line
                else:
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
                    dtstart = parser.parse(value, ignoretz=ignoretz,
                                           tzinfos=tzinfos)
                else:
                    raise ValueError, "unsupported property: "+name
            if (forceset or len(rrulevals) > 1 or
                rdatevals or exrulevals or exdatevals):
                if not parser and (rdatevals or exdatevals):
                    from dateutil import parser
                set = rruleset(cache=cache)
                for value in rrulevals:
                    set.rrule(self._parse_rfc_rrule(value, dtstart=dtstart,
                                                    ignoretz=ignoretz,
                                                    tzinfos=tzinfos))
                for value in rdatevals:
                    for datestr in value.split(','):
                        set.rdate(parser.parse(datestr,
                                               ignoretz=ignoretz,
                                               tzinfos=tzinfos))
                for value in exrulevals:
                    set.exrule(self._parse_rfc_rrule(value, dtstart=dtstart,
                                                     ignoretz=ignoretz,
                                                     tzinfos=tzinfos))
                for value in exdatevals:
                    for datestr in value.split(','):
                        set.exdate(parser.parse(datestr,
                                                ignoretz=ignoretz,
                                                tzinfos=tzinfos))
                if compatible and dtstart:
                    set.rdate(dtstart)
                return set
            else:
                return self._parse_rfc_rrule(rrulevals[0],
                                             dtstart=dtstart,
                                             cache=cache,
                                             ignoretz=ignoretz,
                                             tzinfos=tzinfos)

    def __call__(self, s, **kwargs):
        return self._parse_rfc(s, **kwargs)

rrulestr = _rrulestr()

# vim:ts=4:sw=4:et
