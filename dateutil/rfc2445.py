FREQNAMES = ['YEARLY','MONTHLY','WEEKLY','DAILY','HOURLY','MINUTELY','SECONDLY']

def rrule_to_rfc2445(rule):
    output = []
    h, m, s = [None] * 3
    if rule._dtstart:
        output.append(rule._dtstart.strftime('DTSTART:%Y%m%dT%H%M%S'))
        h, m, s = rule._dtstart.timetuple()[3:6]

    parts = ['FREQ=' + FREQNAMES[rule._freq]]
    if rule._interval != 1:
        parts.append('INTERVAL=' + str(rule._interval))
    if rule._wkst:
        parts.append('WKST=' + str(rule._wkst))
    if rule._count:
        parts.append('COUNT=' + str(rule._count))

    for name, value in [
            ('BYSETPOS', rule._bysetpos),
            ('BYMONTH', rule._bymonth),
            ('BYMONTHDAY', rule._bymonthday),
            ('BYYEARDAY', rule._byyearday),
            ('BYWEEKNO', rule._byweekno),
            ('BYWEEKDAY', rule._byweekday),
            ]:
        if value:
            parts.append(name + '=' + ','.join(str(v) for v in value))

    # Only include these if they differ from rule._dtstart
    if rule._byhour and rule._byhour[0] != h:
        parts.append('BYHOUR=%s' % rule._byhour)
    if rule._byminute and rule._byminute[0] != m:
        parts.append('BYMINUTE=%s' % rule._byminute)
    if rule._bysecond and rule._bysecond[0] != s:
        parts.append('BYSECOND=%s' % rule._bysecond),


    output.append(';'.join(parts))
    return '\n'.join(output)
