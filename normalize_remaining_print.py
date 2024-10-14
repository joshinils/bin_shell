#!/usr/bin/env python3

import glob
import os
import pathlib
import pickle
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


pickled_filename = pathlib.Path(".file_meta.pkl")


def pickle_load_filemeta() -> Dict[str, Tuple[int, int]]:
    try:
        with open(pickled_filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return dict()
    except Exception as e:
        print(type(e), e)
        return dict()


def pickle_save_filemeta(metadata: Dict[str, Tuple[int, int]]) -> None:
    total_streams_path = pathlib.Path(".total_streams_remaining.txt")
    if not metadata:
        try:
            pickled_filename.unlink()
            total_streams_path.unlink()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(type(e), e)
        return

    total_streams_remaining = 0
    for _, meta_tuple in metadata.items():
        total_streams_remaining += meta_tuple[0]

    with open(total_streams_path, "w") as total_streams_file:
        total_streams_file.write(f"{total_streams_remaining}")

    with open(pickled_filename, 'wb') as f:
        pickle.dump(metadata, f)

# for python 3.8
def removesuffix(text: str, suffix: str) -> str:
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def main():
    filenames = next(os.walk(os.getcwd()), (None, None, []))[2]  # [] if no file
    filenames_mkv = next(os.walk(os.getcwd() + os.sep + "Link to makeMKV_out"), (None, None, []))[2]  # [] if no file

    for name in filenames_mkv:
        filenames.append("Link to makeMKV_out/" + name)

    # print()
    to_remove = []
    for name in filenames:
        if name.endswith(".working"):
            to_remove.append(name[:-8])

    to_keep = []
    for name in filenames:
        if name in to_remove:
            continue
        if not name.lower().endswith(extension_keep):
            continue
        to_keep.append(name)

    filemeta_data_old = pickle_load_filemeta()

    filemeta_data = {}
    for filename, meta_tuple in filemeta_data_old.items():
        if filename in to_keep:
            filemeta_data[filename] = meta_tuple

    streams_size_name = []
    for name in to_keep:
        if name not in filemeta_data:
            filemeta_data[name] = (get_amount_of_audio_streams(name), os.path.getsize(name))
        stream_count, filesize = filemeta_data.get(name)
        streams_size_name.append((stream_count, filesize, name))

    pickle_save_filemeta(filemeta_data)

    streams_size_name.sort(key=lambda x: x[1], reverse=False)
    streams_size_name.sort(key=lambda x: x[0], reverse=False)
    if len(streams_size_name) > 0:
        printables = []
        log_names = list(set([removesuffix(fname, ".log") for fname in glob.glob(f"*.working.log") + glob.glob(f"*.working") if os.path.isfile(fname)]))

        max_streams_count = 0
        for log_name in log_names:
            try:
                # during merging there exists the log file of the form
                # "better---Title_year - MD ORT.working.log"
                # which does not have a stream number
                max_streams_count = max(max_streams_count, int(log_name.split(".working")[-2][-3:]) +1)
            except:
                continue

        for stream_count, size, fname in streams_size_name:
            dict_of_integers = {}
            for i in range(max_streams_count):
                dict_of_integers[i] = "·"
            working_now = 0
            for log_name in log_names:
                if log_name.startswith(fname):
                    # get stream number from log_name
                    stream_number = int(log_name.split(".working")[-2][-3:])
                    dict_of_integers[stream_number] = f"@{log_name[:20]} {fname[:20]}#" + str(stream_number)  # [-1]
                    dict_of_integers[stream_number] = str(stream_number)[-1]
                    working_now += 1
            working_now_str = ""
            for i in range(max_streams_count):
                working_now_str += dict_of_integers[i]
            working_now_str = ' ' * (0*max_streams_count - working_now) + working_now_str
            printables.append(f"{stream_count:2d}, {make_size_str(size)}, {working_now_str} {fname.replace('Link to makeMKV_out/', '')}")

        print("Waiting:")
        for line in printables:
            print(line)
    else:
        print("Waiting: None")


if __name__ == "__main__":
    main()
