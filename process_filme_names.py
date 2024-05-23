#!/usr/bin/env python3

import csv
import itertools
import os
import pathlib
import pickle
from collections import defaultdict
from typing import Dict, List, Set, Tuple, TypedDict, Union

import tqdm
from pymediainfo import MediaInfo

pickled_filename = pathlib.Path(".movie_languages_meta.pkl")

def pickle_load_filemeta() -> Dict[str, List[str]]:
    try:
        with open(pickled_filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return dict()
    except Exception as e:
        print(type(e), e)
        return dict()


def pickle_save_filemeta(metadata: Dict[str, List[str]]) -> None:
    with open(pickled_filename, 'wb') as f:
        pickle.dump(metadata, f)


def get_languages(path: str) -> List[str]:
    path = path.rstrip('\n')
    meta = pickle_load_filemeta()

    if path not in meta:
        media_info = MediaInfo.parse(path)
        langs_dict = defaultdict(list)
        for a_track in media_info.audio_tracks:
            d = a_track.to_data()
            langs_dict[d.get('language', d.get('title', 'und'))].append(str(d.get('channel_s', '0')))
        langs_list = []
        for k, v in langs_dict.items():
            langs_list.append(f"{k.upper()}x{'x'.join(v)}")
        meta[path] = langs_list
        pickle_save_filemeta(meta)

    return meta[path]


class InfoDict(TypedDict):
    name: str
    year: Union[int, str]
    versions: Set[str]
    languages: List[str]


def gen_csv(file_name):
    data: Dict[str, Tuple[str, int, Set[str]]] = dict()

    file_lines: List[str] = []

    file_path = pathlib.Path(file_name + ".txt")
    if not file_path.exists():
        return

    with open(file_path, "r") as filme_file:
        for line in filme_file:
            file_lines.append(line.rstrip('\n'))

    if len(file_lines) == 0:
        print(f"ignoring {file_path=}, {len(file_lines)=}, skipping")
        return

    for filename in tqdm.tqdm(file_lines, dynamic_ncols=True, miniters=1):
        for sort_num in range(1000):
            filename = filename.removeprefix(f"{sort_num:>03}")

        for media_type_prefix in [
            "__TV",
            "_MED",
            "_DVD",
            "__BD",
        ]:
            filename = filename.removeprefix(media_type_prefix)

        for media_type_prefix in [
            "bonus",
            "better",
            "again",
            "new",
            "hd-tv-dvd",
        ]:
            filename = filename.removeprefix(media_type_prefix)
            filename = filename.removeprefix("---")

        split_parts = filename.strip().split("/")
        if len(split_parts) == 5:
            _, _, year, _, basename = split_parts
        else:
            for elem in split_parts:
                if elem == "."  or elem == "":
                    continue

                if not (elem.endswith(".mkv") or elem.endswith(".mp4")):
                    continue

                basename = elem
                year = "N/AA"
                for part in elem.split("_"):
                    for part2 in part.split(" - "):
                        if len(part2) != 4:
                            continue
                        if part2.isdigit():
                            year = part2
                            break
                break

        basename, _ = os.path.splitext(basename.lstrip("_"))
        filename_parts = basename.split(f"_{year} - ")
        movie_name = filename_parts[0]

        movie_version = " ".join(filename_parts[1:])
        for i in range(10):
            # remove duplicates because of part1, part2 etc.
            movie_version = movie_version.replace(f" - part{i}", "")
            movie_version = movie_version.replace(f" - part {i}", "")
            movie_version = movie_version.replace(f"- part{i}", "")
            movie_version = movie_version.replace(f"- part {i}", "")
            movie_version = movie_version.replace(f"-part{i}", "")
            movie_version = movie_version.replace(f"-part {i}", "")
            movie_version = movie_version.replace(f" -part{i}", "")
            movie_version = movie_version.replace(f" -part {i}", "")
            movie_version = movie_version.replace(f"part{i}", "")
            movie_version = movie_version.replace(f"part {i}", "")

        movie_key = movie_name + year
        dict_default: InfoDict = {
            "name": movie_name,
            "year": year,
            "versions": set(),
            "languages": get_languages(filename),
        }
        movie_dict = data.get(movie_key, dict_default.copy())
        # print(movie_tuple)
        # print(movie_version, end=""); print(type(movie_version), end=""); print(len(movie_version), end=""); print(type(movie_version[0]))
        movie_dict["versions"].add(movie_version)
        data[movie_key] = movie_dict

    firefox_commands = ""
    with open(file_name + '.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["movie_name", "year", "movie_version", "languages"])
        for movie_key, info_dict in data.items():
            firefox_commands += f"{info_dict['year']} {info_dict['name']}\n"
            csv_writer.writerow([info_dict["name"], info_dict['year'], " *UND* ".join(info_dict['versions']), ";".join(info_dict['languages'])])

    with open(file_name + '.firefox', 'w', newline='') as fox_commands_file:
        fox_commands_file.writelines(firefox_commands)


def main():
    for file_name in ["filme_names", "filme_borked", "filme_neu"]:
        gen_csv(file_name)


if __name__ == "__main__":
    main()
