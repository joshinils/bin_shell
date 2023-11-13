#!/usr/bin/env python3

import datetime
import sys

seconds = float(sys.argv[1].replace(",", "."))
td = datetime.timedelta(seconds=seconds)
d = datetime.datetime(1, 1, 1)

days = 0
while seconds >= 60 * 60 * 24:
    days += 1
    seconds -= 60 * 60 * 24

if days == 0 and seconds < 60:
    val = (d + td).strftime("%H:%M:%S.%f")
    val = val.rstrip("0")
    val = val.rstrip(".")
else:
    val = (d + td).strftime("%H:%M:%S")

if days == 0:
    print(val.lstrip("0:"))
elif days == 1:
    print("1 day,", val)
else:
    print(days, "days", val)
