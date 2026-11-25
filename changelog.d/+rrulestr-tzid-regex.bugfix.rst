Fixed quadratic run time in ``rrulestr`` on input with many ``TZID=`` substrings and no ``:`` after them, where a 156 KiB string took about 30 seconds to reject. Reported and fixed by @varun3257.
