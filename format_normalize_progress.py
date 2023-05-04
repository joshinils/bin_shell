#!/usr/bin/env python3

import datetime
import math
import os
import re
import sys
from typing import Tuple

import colorama


def round_nearest(x, a):
    # https://stackoverflow.com/a/28427814
    max_frac_digits = 100
    for i in range(max_frac_digits):
        if round(a, -int(math.floor(math.log10(a))) + i) == a:
            frac_digits = -int(math.floor(math.log10(a))) + i
            break
    return round(round(x / a) * a, frac_digits)


def fix_time_format(input: str) -> datetime.timedelta:
    if input == "?":
        return datetime.timedelta(days=1, seconds=-1)

    parts = input.split(":")

    r_parts = list(reversed(parts)) + ["00"] + ["00"]
    seconds, minutes, hours, days, *_ = r_parts

    delta = datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))

    return delta


def calc_time_done(time_done: datetime.datetime, iteration_time: float) -> Tuple[datetime.datetime, float]:
    time_done = time_done.timestamp()
    delta_nearest = time_done - round_nearest(time_done, iteration_time)
    time_done = round_nearest(time_done, iteration_time)
    time_done = datetime.datetime.fromtimestamp(time_done)
    return time_done, delta_nearest


def get_small_bar(percentage: float, width_chars: int) -> str:
    percentage = max(0, min(percentage, 100))
    width_chars = int(width_chars - 1)
    width_filled = percentage * width_chars / 100
    decimal = (width_filled - int(width_filled)) * 8
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

    second_half_width = math.ceil(width_chars / 2)
    stream_width = math.floor(second_half_width / total_stream)

    streams_done_count = current_stream - 1
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
    inner = f"{first_half}{separator}{second_half}"
    while len(inner) < width_chars:
        inner = "█" + inner
    return f"{inner}"


def trunc_filename(filename: str) -> str:
    if filename.endswith(".log"):
        filename = filename[:-4]
    if filename.endswith(".mp4"):
        filename = filename[:-4]
    if filename.endswith(".mkv"):
        filename = filename[:-4]

    return filename


def format_timedelta(delta: datetime.timedelta) -> str:
    seconds = delta.seconds

    minutes = seconds // 60
    seconds -= minutes * 60

    hours = minutes // 60
    minutes -= hours * 60

    if delta.days > 0:
        return f"{delta.days: >2}:{hours:02}:{minutes:02}:{seconds:02}"
    elif hours > 0:
        return f"   {hours: >2}:{minutes:02}:{seconds:02}"
    elif minutes > 0:
        return f"      {minutes: >02}:{seconds:02}"
    return f"         {seconds: >2}"


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
        matches = regex.findall(line)
        stream_or_passes: str
        stream_current_str: str
        stream_total_str: str
        percent_done_str: str
        time_elapsed_str: str
        time_remaining_str: str
        iteration_time_str: str
        it_s_it: str
        title: str

        stream_or_passes, stream_current_str, stream_total_str, percent_done_str, time_elapsed_str, time_remaining_str, iteration_time_str, it_s_it, title, *_ = matches[0]

        try:
            iteration_time = float(iteration_time_str)
        except Exception:
            iteration_time = 100.0

        try:
            percent_done = float(percent_done_str)
        except Exception:
            percent_done = 1.0

        try:
            stream_current = int(stream_current_str)
            stream_total = int(stream_total_str)
        except Exception:
            stream_current = 1
            stream_total = 100

        title = trunc_filename(title)

        total_percent = percent_done / 2 + 50
        time_elapsed = fix_time_format(time_elapsed_str)
        time_remaining = fix_time_format(time_remaining_str)

        stream_num = ""
        if stream_or_passes == "Stream ":
            stream_num = f"{stream_current:2}/{stream_total:2}"
            time_per_stream = time_elapsed + time_remaining
            streams_left = stream_total - stream_current

            total_percent = ((stream_current - 1) * 100 + percent_done) / stream_total / 2

            total_time_left = time_remaining + time_per_stream * streams_left + stream_total * time_per_stream
            if percent_done <= 2:
                total_time_left += datetime.timedelta(hours=stream_total)
        elif stream_or_passes == "Second Pass":
            total_time_left = time_remaining
            if percent_done <= 2:
                total_time_left += datetime.timedelta(hours=1)

        datetime_done = datetime.datetime.now() + total_time_left

        datetime_done, delta_nearest = calc_time_done(datetime_done, iteration_time)
        time_done_str = f"{datetime_done}"[:19]
        if it_s_it == "it/s":
            time_str = f"{time_done_str} " + " " * 8
        else:
            time_str = f"{time_done_str} {delta_nearest:+8.2f}"

        import shutil
        width, height = shutil.get_terminal_size((80, 20))

        filenames = next(os.walk(os.getcwd()), (None, None, []))[2]  # [] if no file

        name_length = 0
        for name in filenames:
            if not name.endswith(".log"):
                continue
            name_length = max(name_length, len(trunc_filename(name)))

        bar_width = width - name_length - 37  # TODO: CHECK IF RIGHT?

        percentage_bar = get_percentage_bar(total_percent, bar_width, stream_current, stream_total)
        # time_left = datetime_done - datetime.datetime.now()
        # seconds_left = max(0, min(round_nearest(time_left.seconds + time_left.days * 60 * 60 * 24, iteration_time), 99999))
        # info_one = f"{seconds_left:05.0f} {time_str} {format_timedelta(total_time_left)} {total_percent:5.1f}%"

        percent_small = ""
        if percent_done <= 9:
            percent_small = f" {percent_done}"

        info_one = f"{format_timedelta(total_time_left)} {time_str} {total_percent:5.1f}%{percent_small}"
        info_one = info_one.replace(datetime.datetime.now().strftime('%Y-%m-%d'), " " * 10)
        info_two = f"{title.rjust(name_length)}"
        extra_info = f"{stream_num} {time_elapsed_str.rjust(8)} < {time_remaining_str.rjust(8)}{iteration_time:8.2f} {it_s_it} "

        # if total_percent < 50:
        #     extra_info = extra_info[::-1]
        #     percentage_bar = percentage_bar[::-1]

        if len(info_one) < width:
            info = info_one
            percentage_bar = get_percentage_bar(total_percent, width, stream_current, stream_total)
            if len(info_one) + len(info_two) < width:
                if len(info_one) + len(info_two) + len(extra_info) >= width:
                    extra_info = ""

                normal_info = info_one.ljust(width - len(info_two) - len(extra_info)) + extra_info + info_two
                info = normal_info

        if len(info) <= len(percentage_bar):
            percentage_bar = list(percentage_bar)

            for i, (p, e) in enumerate(zip(percentage_bar[::-1], info[::-1])):
                if e == " ":
                    continue
                elif p == " ":
                    percentage_bar[len(percentage_bar) - i - 1] = e  # white black
                elif p == "█":
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.BLACK + colorama.Back.WHITE   + e + colorama.Style.RESET_ALL  # noqa: E221
                elif p == "▏":  # 1
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.CYAN  + colorama.Back.BLACK   + e + colorama.Style.RESET_ALL  # noqa: E221
                elif p == "▎" or p == "▍":  # 2 or 3
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.CYAN  + colorama.Back.BLUE    + e + colorama.Style.RESET_ALL  # noqa: E221
                elif p == "▌":  # 4
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.CYAN  + colorama.Back.MAGENTA + e + colorama.Style.RESET_ALL  # noqa: E221
                elif p == "▋" or p == "▊":  # 5 or 6
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.BLUE  + colorama.Back.CYAN    + e + colorama.Style.RESET_ALL  # noqa: E221
                elif p == "▉":  # 7
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.BLUE  + colorama.Back.WHITE   + e + colorama.Style.RESET_ALL  # noqa: E221
                else:
                    percentage_bar[len(percentage_bar) - i - 1] = colorama.Fore.BLACK + colorama.Back.YELLOW  + e + colorama.Style.RESET_ALL  # noqa: E221

            percentage_bar = "".join(percentage_bar)

        print(f"{percentage_bar}")


if __name__ == "__main__":
    main()
