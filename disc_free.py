#!/usr/bin/env python3

import inspect
import os
import shutil


def find_mount_point(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path


def getmount(path):
    path = os.path.realpath(os.path.abspath(path))
    while path != os.path.sep:
        if os.path.ismount(path):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    return path


abs_path = os.path.abspath((inspect.stack()[0])[1])
directory_of_1py = os.path.dirname(abs_path)
cwd = os.getcwd()

mount_point = find_mount_point(cwd)
mount = getmount(cwd)

total, used, free = shutil.disk_usage(cwd)


def concat_size_tuple(tup) -> str:
    return f"{tup[0]:5}{tup[1]}"


def make_size_str(size_B: int) -> str:
    if size_B == 0:
        return "0B"

    name_size_binary = {
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

    # name_size_decimal = {
    #     "B":  10 ** 00,  # noqa: E241
    #     "KB": 10 **  3,  # noqa: E222
    #     "MB": 10 **  6,  # noqa: E222
    #     "GB": 10 **  9,  # noqa: E222
    #     "TB": 10 ** 12,
    #     "PB": 10 ** 15,
    #     "EB": 10 ** 18,
    #     "ZB": 10 ** 21,
    #     "YB": 10 ** 24,
    # }

    name_size = name_size_binary

    name_size_B = []

    do_continue = True
    for name, size in reversed(name_size.items()):
        if size > size_B and do_continue:
            continue
        do_continue = False
        this_value = size_B // size
        name_size_B.append((this_value, name))
        size_B -= this_value * size

    res = concat_size_tuple(name_size_B.pop(0))

    while len(name_size_B) > 0:
        res += concat_size_tuple(name_size_B.pop(0))

    return res


totalstr = make_size_str(total)
used_str = make_size_str(used)
free_str = make_size_str(free)

longest_str_size = max(len(totalstr), len(used_str), len(free_str))

mount_info = mount

if mount_point != mount:
    mount_info += " " + mount_point

print("total", totalstr.rjust(longest_str_size), mount_info)
print("used ", used_str.rjust(longest_str_size) + f"{used / total * 100:10.5f}%")
print("free ", free_str.rjust(longest_str_size) + f"{free / total * 100:10.5f}%")
