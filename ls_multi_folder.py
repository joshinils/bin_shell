#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys
from typing import List, Set, Tuple


def print_folder_content(folder):
    if os.path.isdir(folder):
        files = []
        for root, dirs, filenames in os.walk(folder):
            for filename in filenames:
                ext: str = os.path.splitext(filename)[1]
                if ext.lower() in ['.mp4', '.mkv', '.mov']:
                    files.append(os.path.join(root, filename))

        if len(files) > 0:
            print(f"{folder}: {len(files)}")
            for file in files:
                name = os.path.basename(file)
                size_bytes = os.stat(file).st_size
                size_human = subprocess.check_output(['numfmt', '--to=iec', str(size_bytes)]).decode().strip()
                print(f"{name}\t{size_human}\t{size_bytes}")
        else:
            print(f"{folder}: empty")


def print_folders_contents(folders: List[str]):
    filenames_superset: Set[str] = set()
    filecount_each: List[Tuple[str, int]] = []
    for folder in folders:
        filecount = 0
        if os.path.isdir(folder):
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    ext: str = os.path.splitext(filename)[1]
                    if ext.lower() in ['.mp4', '.mkv', '.mov']:
                        filecount += 1
                        filenames_superset.add(filename.replace(".normalized.mkv", ""))
                break  # do not descent into next subfolders
        filecount_each.append((folder, filecount))

    # for file in filenames_superset:
    #     print(file)
    # exit()

    if len(filenames_superset) == 0:
        print(f"{': empty, '.join(folders)}: empty")
        return

    filecount_each.sort(key=lambda x: x[1], reverse=True)

    foldername: str
    folder_counts = "\t"
    for foldername, count in filecount_each:
        foldername = str(foldername).replace("normalized_", "")
        folder_counts += f"{foldername}\t{count}\t"
    print(folder_counts)

    filecount_each = [(file, count) for file, count in filecount_each if count > 0]  # do not print dots for empty dir

    for file in sorted(filenames_superset):
        name = os.path.basename(file)
        output = f"{name}"
        # print(file)
        for folder, count in filecount_each:
            file_name = folder + os.sep + name
            # print(file_name, folder, name)
            if not pathlib.Path(file_name).is_file():
                file_name = pathlib.Path(file_name + ".normalized.mkv")
                if not file_name.is_file():
                    output += "\t.\t."
                    continue
            size_bytes = os.stat(file_name).st_size
            size_human = subprocess.check_output(['numfmt', '--to=iec', str(size_bytes)]).decode().strip()
            output += f"\t{size_human}\t{size_bytes}"
        print(output)
        # print()


def main():
    print_folders_contents([pathlib.Path("normalized"), pathlib.Path("normalized_done"), pathlib.Path("normalized_temp"), pathlib.Path("normalized_temp_single")])


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        exit()

    if len(sys.argv) == 2:
        print_folder_content(sys.argv[1])
        print()
    else:
        print_folders_contents(sys.argv[1:])
