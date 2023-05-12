#!/usr/bin/env python3

import os
from typing import Dict, Tuple

from normalize import get_amount_of_audio_streams

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
        "B":  10 ** 00,  # noqa: E241
        "KB": 10 **  3,  # noqa: E222
        "MB": 10 **  6,  # noqa: E222
        "GB": 10 **  9,  # noqa: E222
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

    streams_size_name = []
    for name in to_keep:
        streams_size_name.append((get_amount_of_audio_streams(name), os.path.getsize(name), name))

    streams_size_name.sort(key=lambda x: x[1], reverse=False)
    streams_size_name.sort(key=lambda x: x[0], reverse=False)
    print("Waiting:")
    for stream_count, size, name in streams_size_name:
        print(f"{stream_count:2d}, {make_size_str(size)}, {name}")


if __name__ == "__main__":
    main()
