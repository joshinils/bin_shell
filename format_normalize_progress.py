#!/usr/bin/env python3

import sys
import re
import datetime
import math
from typing import Tuple
import os


def round_nearest(x, a):
    # https://stackoverflow.com/a/28427814
    max_frac_digits = 100
    for i in range(max_frac_digits):
        if round(a, -int(math.floor(math.log10(a))) + i) == a:
            frac_digits = -int(math.floor(math.log10(a))) + i
            break
    return round(round(x / a) * a, frac_digits)

def fix_time_format(input: str) -> str:
    ret = "00:00:00"
    try:
        if input == "?":
            raise ValueError()
        input = "00000" + input
        input = list(input[-8:])
        input[-6] = ":"
        ret = "".join(input)
    except:
        pass

    return ret


def calc_time_done(time_done: datetime.datetime, iteration_time: float) -> Tuple[datetime.datetime, float]:
    time_done = time_done.timestamp()
    delta_nearest = time_done - round_nearest(time_done, iteration_time)
    time_done = round_nearest(time_done, iteration_time)
    time_done = datetime.datetime.fromtimestamp(time_done)
    return time_done, delta_nearest

def get_small_bar(percentage: float, width_chars: int) -> str:
    percentage = max(0, min(percentage, 100))
    width_chars = int(width_chars-1)
    width_filled = percentage * width_chars / 100
    decimal = (width_filled - int(width_filled))*8
    # print(f"{percentage=}, {decimal=}")
    bar = " ▏▎▍▌▋▊▉█"
    if int(decimal) < 1:
        decimal_str = " "
        if decimal == 0:
            decimal_str = ""
        offset = 0
    else:
        offset = -0
        decimal_str = bar[int(decimal)]
    return "█" * int(width_filled + offset) + decimal_str + " " * int(width_chars - width_filled)

def get_percentage_bar(percentage: float, width_chars, current_stream=1, total_stream=1) -> str:
    light = "░"
    medium = "▒"
    dark = "▓"
    second_half_width = math.ceil(width_chars/2)
    stream_width = math.ceil(second_half_width / total_stream -1)

    streams_done_count = current_stream -1
    streams_todo_count = total_stream - current_stream

    sub_first = get_small_bar(percentage * 2 * total_stream - (current_stream - 1) * 100, stream_width)
    if percentage >= 50:
        sub_first = medium
        streams_done_count = 1
        separator = dark

    streams_done = dark.join([get_small_bar(100, stream_width)] * streams_done_count)
    streams_todo = light.join([get_small_bar(0, stream_width)] * streams_todo_count)

    if len(streams_done) > 0:
        streams_done += dark
    if len(streams_todo) > 0:
        streams_todo = light + streams_todo

    first_half = streams_done + sub_first + streams_todo
    second_half = get_small_bar(percentage * 2 - 100, second_half_width)
    if percentage < 50:
        second_half = get_small_bar(0, second_half_width)
        separator = light
    else:
        offset_for50 = 0
        if total_stream > 1:
            offset_for50 = -1
        first_half = get_small_bar(100, second_half_width + offset_for50)
    return f"|{first_half}{separator}{second_half}|"

def main() -> None:
    # hundred=200
    # for i in range(101):
    #     print(f"{i:03}#{get_small_bar(i, hundred)}#")
    # print()
    # print()
    # for i in range(0, 17, 1):
    #     print(f"{i:03}", get_percentage_bar(i, hundred, 1, 3))
    # print()
    # for i in range(17, 34, 1):
    #     print(f"{i:03}", get_percentage_bar(i, hundred, 2, 3))
    # print()
    # for i in range(34*2, 55*2, 1):
    #     print(f"{i/2:03}", get_percentage_bar(i/2, hundred, 3, 3))
    # # print()
    # for i in range(50, 101, 1):
    #     print(f"{i:03}", get_percentage_bar(i, hundred, 1, 1))
    # exit()

    reg_str = r"""(Stream |Second Pass)(?:(\d+)\/(\d+))*: +\d+%\|[ ▏▎▍▌▋▊▉█]{10}\| +(\d+)\/100 \[([\d:,\?]+)<([\d:,\?]+), +([\d\.,?]+)(it\/s|s\/it)\](?:.*)\./(.*)\.log"""
    regex = re.compile(reg_str)

    for line in sys.stdin:
        # print(line)
        matches = regex.findall(line)
        stream_or_passes, stream_current, stream_total, percent_done, time_elapsed, time_remaining, iteration_time, it_s_it, title, *_ = matches[0]

        try:
            iteration_time = float(iteration_time)
        except:
            iteration_time = 1

        try:
            percent_done = float(percent_done)
        except:
            percent_done = 1

        try:
            stream_current = int(stream_current)
            stream_total = int(stream_total)
        except:
            stream_current = 1
            stream_total = 1

        total_percent = percent_done/2 + 50
        time_elapsed = fix_time_format(time_elapsed)
        time_remaining = fix_time_format(time_remaining)

        remaining = datetime.datetime.strptime(time_remaining, '%H:%M:%S')
        remaining = datetime.timedelta(0, hours=remaining.hour, minutes=remaining.minute, seconds=remaining.second)

        if stream_or_passes == "Stream ":
            elapsed_t = datetime.datetime.strptime(time_elapsed, '%H:%M:%S')
            elapsed_t = datetime.timedelta(0, hours=elapsed_t.hour, minutes=elapsed_t.minute, seconds=elapsed_t.second)
            time_per_stream = elapsed_t + remaining
            streams_left = stream_total - stream_current

            total_percent = ((stream_current - 1) * 100 + percent_done) / stream_total / 2

            time_done = datetime.datetime.now() + remaining + time_per_stream * streams_left + stream_total * time_per_stream
        elif stream_or_passes == "Second Pass":
            time_done = datetime.datetime.now() + remaining

        time_done, delta_nearest = calc_time_done(time_done, iteration_time)
        time_done = f"{time_done}.00"[:22]
        if it_s_it == "it/s":
            time_str = f"{time_done}        "
        else:
            time_str = f"{time_done} {delta_nearest:+7.2f}"

        import shutil
        width, height = shutil.get_terminal_size((80, 20))

        filenames = next(os.walk(os.getcwd()), (None, None, []))[2]  # [] if no file

        name_length = 0
        for name in filenames:
            if name.endswith(".log"):
                name_length = max(name_length, len(name)-4)

        bar_width = width - name_length - 41
        print(bar_width, width)
        print(f"{time_str}, {total_percent:4.1f}%, {get_percentage_bar(total_percent, bar_width, stream_current, stream_total)} {title}")

if __name__ == "__main__":
    main()
