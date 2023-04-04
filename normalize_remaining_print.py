#!/usr/bin/env python3

import os
from typing import Tuple, Dict
import subprocess

extension_keep: Tuple[str] = (
    "ogg",
    "m4a",
    "opus",
    "webm",
    "mp4",
    "mkv",
)


def make_size_str(size_B: int) -> str:
    if size_B == 0:
        return "   0.0    B"

    name_size_binary: Dict[str, int] = {
        #  "B":   2 ** 00,
        #      since disc usage is at a minimum 4Kib, even for a one byte file,
        #      so it doesn't make sense to add a trailing 0 for everything
        "KiB": 2 ** 10,
        "MiB": 2 ** 20,
        "GiB": 2 ** 30,
        "TiB": 2 ** 40,
        "PiB": 2 ** 50,
        "EiB": 2 ** 60,
        "ZiB": 2 ** 70,
        "YiB": 2 ** 80,
    }

    name_size_decimal: Dict[str, int] = {
        "B":  10 ** 00,
        "KB": 10 **  3,
        "MB": 10 **  6,
        "GB": 10 **  9,
        "TB": 10 ** 12,
        "PB": 10 ** 15,
        "EB": 10 ** 18,
        "ZB": 10 ** 21,
        "YB": 10 ** 24,
    }

    name_size = name_size_decimal
    name_size = name_size_binary

    for name, size in reversed(name_size.items()):
        if size > size_B:
            continue
        return f"{size_B / size:7.2f} {name}"

def main():
    filenames = next(os.walk(os.getcwd()), (None, None, []))[2]  # [] if no file

    # print()
    to_remove = []
    for name in filenames:
        if name.endswith(".log"):
            to_remove.append(name[:-4])

    to_keep = []
    for name in filenames:
        if name.endswith(".log"):
            continue
        if name in to_remove:
            continue
        if not name.endswith(extension_keep):
            continue
        to_keep.append(name)

    size_name = []
    for name in to_keep:
        process_ffprobe = subprocess.Popen(["ffprobe", "-i", name, "-show_streams", "-select_streams", "a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_grep = subprocess.Popen(["grep", "channels"], stdin=process_ffprobe.stdout, stdout=subprocess.PIPE)
        output, error = process_grep.communicate()
        result = output.decode().strip()
        process_ffprobe = subprocess.Popen("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1".split() + [name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process_ffprobe.communicate()
        duration = float(output)
        print(duration)


        audio_channels: Dict[int, int] = {2:0, 6:0}
        channels_count = 0
        for line in result.split("channels="):
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                try:
                    num_channels = int(stripped_line)
                    audio_channels[num_channels] = audio_channels.get(num_channels, 0) + 1
                    channels_count += num_channels
                except:
                    pass
        print(audio_channels)

        size_name.append((os.path.getsize(name), name, audio_channels, channels_count, duration))

    size_name.sort(key=lambda x: x[3] * x[4], reverse=True)

    print("Waiting:")
    for size, name, channels_dict, num_channels, duration in size_name:
        print(f"{make_size_str(size)}, {str(channels_dict): >12}={num_channels: >2g} {name}")


if __name__ == "__main__":
    main()
