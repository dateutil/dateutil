"""
Copyright (c) 2003-2005  Gustavo Niemeyer <gustavo@niemeyer.net>

This module offers extensions to the standard python 2.3+
datetime module.
"""
__author__ = "Gustavo Niemeyer <gustavo@niemeyer.net>"
__license__ = "PSF License"

import datetime
import thread
import signal
import time

class sched:

    def __init__(self, rrule,
                 tolerance=None, last=None,
                 execute=None, args=None, kwargs=None):
        self._rrule = rrule
        if tolerance:
            self._tolerance = datetime.timedelta(seconds=tolerance)
        else:
            self._tolerance = None
        self._last = last
        self._execute = execute
        self._args = args or ()
        self._kwargs = kwargs or {}

    def last(self):
        return self._last

    def next(self, now=None):
        if not now:
            now = datetime.datetime.now()
        return self._rrule.after(now)

    def check(self, now=None, readonly=False):
        if not now:
            now = datetime.datetime.now()
        item = self._rrule.before(now, inc=True)
        if (item is None or item == self._last or
            (self._tolerance and item+self._tolerance < now)):
            return None
        if not readonly:
            self._last = item
            if self._execute:
                self._execute(*self._args, **self._kwargs)
        return item


class schedset:
    def __init__(self):
        self._scheds = []

    def add(self, sched):
        self._scheds.append(sched)

    def next(self, now=None):
        if not now:
            now = datetime.datetime.now()
        res = None
        for sched in self._scheds:
            next = sched.next(now)
            if next and (not res or next < res):
                res = next
        return res

    def check(self, now=None, readonly=False):
        if not now:
            now = datetime.datetime.now()
        res = False
        for sched in self._scheds:
            if sched.check(now, readonly):
                res = True
        return res


class schedthread:
    
    def __init__(self, sched, lock=None):
        self._sched = sched
        self._lock = lock
        self._running = False

    def running(self):
        return self._running

    def run(self):
        self._running = True
        thread.start_new_thread(self._loop, ())
        
    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            if self._lock:
                self._lock.acquire()
            now = datetime.datetime.now()
            self._sched.check(now)
            if self._lock:
                self._lock.release()
            seconds = _seconds_left(self._sched.next(now))
            if seconds is None:
                self._running = False
                break
            if self._running:
                time.sleep(seconds)


class schedalarm:
    
    def __init__(self, sched, lock=None):
        self._sched = sched
        self._lock = lock
        self._running = False

    def running(self):
        return self._running

    def run(self):
        self._running = True
        signal.signal(signal.SIGALRM, self._handler)
        self._handler(None, None)
        
    def stop(self):
        self._running = False

    def _handler(self, sig, frame):
        while self._running:
            if self._lock:
                self._lock.acquire()
            now = datetime.datetime.now()
            self._sched.check(now)
            if self._lock:
                self._lock.release()
            if self._running:
                seconds = _seconds_left(self._sched.next(now))
                if seconds:
                    signal.alarm(seconds)
                    break
                elif seconds is None:
                    self._running = False
                    break


def _seconds_left(next):
    if not next:
        return None
    now = datetime.datetime.now()
    delta = next-now
    seconds = delta.days*86400+delta.seconds
    if seconds < 0:
        seconds = 0
    return seconds

