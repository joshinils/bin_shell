#!/usr/bin/env python3
import argparse
import glob
import os
import pathlib
import typing
from collections import defaultdict


def get_files_here() -> typing.Iterator[str]:
    listdir = os.listdir(os.getcwd())
    for filename in listdir:
        if os.path.isfile(filename):
            yield filename


def main(min_per_folder):
    filenames = list(get_files_here())
    len_dicts: typing.Dict[int, typing.DefaultDict[typing.Set, str]] = {}
    longest_s = 0
    for i in range(1, len(max(filenames, key=len))+1):
        dict_set = defaultdict(set)
        for filename in sorted(filenames):
            dict_set[filename[:i]].add(filename)
        if len(dict_set) > 1 and len(dict_set) < len(filenames):
            for key, elem in dict_set.items():
                if len(elem) < min_per_folder:
                    break
            else:
                longest_s = len(dict_set)
                len_dicts[len(dict_set)] = dict_set

    if longest_s == 0:
        print(f"No suitable folders found for length {min_per_folder} or more files. Exiting.]")
        return
    use_keys = len_dicts[longest_s]

    print(len(use_keys))
    for key, elem in use_keys.items():
        print(f"{key=}", len(elem))
        pathlib.Path(key).mkdir(exist_ok=True, parents=False)

        globbed_files = [fname for fname in glob.glob(f"{key}*") if os.path.isfile(fname)]
        for file in globbed_files:
            pathlib.Path(file).rename(f"{key}/{file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='looks at the beginning of files names, and sorts them into folders with equal beginnings')
    parser.add_argument(
        "min_per_folder",
        type=int,
        help='minimum number of files in any folder',
        metavar="m",
        default=1,
    )
    args = parser.parse_args()
    min_per_folder = args.min_per_folder
    main(min_per_folder)
