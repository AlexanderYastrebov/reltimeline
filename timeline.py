#!/usr/bin/env python
import sys
import json
import csv
from datetime import datetime, timedelta, date


def main():
    read_relations(sys.argv[1], '_srcId')


def read_relations(filename, key_field):
    all_dates = {}
    with open(filename) as f:
        for line in f:
            if not line.strip():
                continue

            rel = json.loads(line)
            key = rel[key_field]

            since = rel['_since']
            actual = rel['_actual']
            share = rel['shareAmount']

            dates = all_dates.get(key, [])
            dates.append((since, actual, share))
            all_dates[key] = dates

    # sort
    for key, dates in all_dates.iteritems(): 
        all_dates[key] = sorted(dates, cmp=cmp_intervals)

    # merge
    for key, dates in all_dates.iteritems():
        all_dates[key] = reduce(merge_intervals, dates, [])

    timeline = make_timeline(all_dates)

    # format dates
    for key, dates in all_dates.iteritems():
        all_dates[key] = format_dates(dates)

    print {'dates': all_dates, 'timeline': timeline}


def cmp_intervals(i1, i2):
    x = i1[0] - i2[0]
    if x != 0:
        return x
    return i1[1] - i2[1]


def merge_intervals(agg, i):
    if not agg:
        return [i]
    last = agg[-1]
    # actual1 >= since2 and share1 == share2
    if last[1] >= i[0] and last[2] == i[2]:
        return agg[:-1] + [(min(last[0], i[0]), max(last[1], i[1]), i[2])]
    else:
        return agg + [i]


def format_dates(dates):
    result = []
    for d in dates:
        result.append((format_ts(d[0]), format_ts(d[1])) + d[2:])
    return result


def format_ts(d):
    return '{0.day:02}.{0.month:02}.{0.year}'.format(date.fromtimestamp(d/1000))


def make_timeline(all_dates):
    dates = []
    for key, values in all_dates.iteritems():
        for d in values:
            if d[0] not in dates:
                dates.append(d[0])
            if d[1] not in dates:
                dates.append(d[1])
    dates.sort()
    result = []
    for d in dates:
        result.append(format_ts(d))
    return result


if __name__ == '__main__':
    main()
