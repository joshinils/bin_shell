#!/usr/bin/env python3
import math
import os
import sys
import typing

import numpy as np

# sizes in [B]ytes

# TODO: fix amount of buckets
# TODO: print heder for files and dirs, not the trailing two chars in 0.f and 0.d


def sum_dir_size(directory: str) -> int:
    size_sum = 0
    for (dirpath, dirnames, filenames) in os.walk(directory, followlinks=False):
        for file_name in filenames:
            if os.path.isfile(dirpath + os.sep + file_name):
                size_sum += os.path.getsize(dirpath + os.sep + file_name)

    return size_sum


# round up, so first digit is one higher
def round_first_digit_up(num: int) -> int:
    if num == 0:
        return 1
    prev_pow_10 = 10 ** math.floor(math.log10(num))
    return math.ceil(num / prev_pow_10) * prev_pow_10


# round first digit, rest 0
def round_first_digit(num: int) -> int:
    if num == 0:
        return 0
    prev_pow_10 = 10 ** math.floor(math.log10(num))
    return round(num / prev_pow_10) * prev_pow_10


def humanize_filesize(size_in_bytes) -> str:
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(size_in_bytes) < 1000:
            return "{:1g}".format(size_in_bytes) + str(unit) + "B"
        size_in_bytes /= 1000
    return str(size_in_bytes) + "B"


def get_buckets(name_size_dict: typing.Dict) -> typing.List[int]:
    max_val = max(name_size_dict.values())
    min_val = min(name_size_dict.values())

    val_different = math.ceil(math.log2(len(file_sizes) + len(dir_sizes)))
    val_different = max(val_different, 10)

    ls = np.logspace(np.log10(round_first_digit_up(min_val)), np.log10(round_first_digit_up(max_val)), val_different)

    buckets = []
    for num in ls:
        buckets.append(round_first_digit(num))

    return buckets


def get_bucketizes_sizes(name_size_dict: typing.Dict, buckets: typing.List[int]) -> typing.List[typing.Tuple[str, str]]:
    bucketized_sizes = {}
    for bucket_size in buckets:
        bucketized_sizes[bucket_size] = 0

    for _, size in name_size_dict.items():
        for bucket_size in buckets:
            if size > bucket_size:
                continue
            else:
                bucketized_sizes[bucket_size] += 1
                break

    printable_arr_sizes = []
    printable_arr_amount = []
    max_length_sizes = 0
    max_length_amount = 0
    for size, amount in bucketized_sizes.items():
        printable_arr_sizes.append(str(humanize_filesize(size)))
        printable_arr_amount.append(str(amount))

        max_length_sizes = max(max_length_sizes, len(printable_arr_sizes[-1]))
        max_length_amount = max(max_length_amount, len(printable_arr_amount[-1]))

    returnable = []
    for size, amount in zip(printable_arr_sizes, printable_arr_amount):
        returnable.append((size.rjust(max_length_sizes), amount.rjust(max_length_amount)))

    return returnable


working_directory = sys.argv[1]

file_names = []
dir_names = []
for (dirpath, dirnames, filenames) in os.walk(working_directory, followlinks=False):
    file_names.extend(filenames)
    dir_names.extend(dirnames)
    break

actual_files = []
for file_name in file_names:
    if os.path.isfile(file_name):
        actual_files.append(file_name)

actual_dirs = []
for dir_name in dir_names:
    if os.path.isdir(dir_name):
        actual_dirs.append(dir_name)

file_names = actual_files
dir_names = actual_dirs

# print(file_names)
# print()

# print(dir_names)
# print()

file_sizes = {}
for file_name in file_names:
    file_sizes[file_name] = os.path.getsize(file_name)

dir_sizes = {}
for dir_name in dir_names:
    dir_sizes[dir_name] = sum_dir_size(dir_name)

both_sizes = {**file_sizes, **dir_sizes}
buckets = get_buckets(both_sizes)

file_l = get_bucketizes_sizes(file_sizes, buckets)
dir_l = get_bucketizes_sizes(dir_sizes, buckets)

has_files = len(file_sizes) > 0
has_dirs = len(dir_sizes) > 0


# TODO: omit all but last line of all 0s

if has_files and has_dirs:
    for a, b in zip(file_l, dir_l):
        name = a[0]
        file_count = a[1]
        dir_count = b[1]
        print(name, ":", file_count + ".f", dir_count + ".d")
elif has_files and not has_dirs:
    for name, file_count in file_l:
        print(name, ":", file_count + ".f")
elif not has_files and has_dirs:
    for name, dir_count in dir_l:
        print(name, ":", dir_count + ".d")
else:
    print("there are no files and no directories")
