#!/usr/bin/env python3

import pathlib
from collections import defaultdict
from typing import List
from tap import Tap
import subprocess
import json


class TArgumentParser(Tap):
    paths: List[pathlib.Path]  # path(s) to file(s)

    def configure(self):
        self.add_argument('paths', nargs="+")


def get_mkvmerge_json(path: pathlib.Path) -> dict:
    cmd = ["mkvmerge", "-J", str(path)]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing mkvmerge: {e}")
        raise Exception
    return json.loads(result.stdout)


def main(path: pathlib.Path) -> None:
    langs_dict = defaultdict(list)

    metadata_json = get_mkvmerge_json(path).get("tracks", {})
    elem: dict
    for elem in metadata_json:
        if elem.get("type") != "audio":
            continue
        # print(type(elem), elem)

        flag_visual_impaired = elem.get("properties", {}).get("flag_visual_impaired")
        flag_commentary = elem.get("properties", {}).get("flag_commentary")
        language = elem.get("properties", {"language_ietf": "und"}).get("language_ietf", "und")
        channel_count = elem.get("properties", {"audio_channels": 0}).get("audio_channels", 0)

        if language == "und":
            language = elem.get("properties", {"language": "und"}).get("language", "und")
            if language == "ger":
                language = "de"
            elif language == "eng":
                language = "en"
            elif language == "und":
                pass
            else:
                print(f"{language=} found, not sure what to do with it.")

        if flag_commentary:
            language += "-co"
        if flag_visual_impaired:
            language += "-vi"
        language += f"*{channel_count}"

        format = elem.get("codec")
        # print(f"{flag_commentary=} {flag_visual_impaired=} {language=} {format=}")

        print(f"{format=}")
        langs_dict[language].append(f"{format}")
        print()

    items_multi = []
    items_single = []
    total_multi_streams = 0
    total_single_streams = 0
    de = False
    en = False
    for lang_code, stream_type in langs_dict.items():
        print(lang_code, len(stream_type))
        de = lang_code.split("*")[0] == "de" or de
        en = lang_code.split("*")[0] == "en" or en
        if len(stream_type) > 1 or lang_code == "und":  # or "d=" in v[0]:
            items_multi.append(f"{len(stream_type)}×{lang_code}[{', '.join(stream_type)}]")
            if "-co" in lang_code:
                continue
            total_multi_streams += len(stream_type)
        elif len(stream_type) <= 1 or lang_code == "und":
            items_single.append(f"{len(stream_type)}×{lang_code}[{', '.join(stream_type)}]")
            total_single_streams += len(stream_type)

    path_str = ""

    print(items_multi)
    print(items_single)

    path_str += ", ".join(sorted(items_multi) + sorted(items_single))

    de_en_both = ""
    if en is False and de is False:
        de_en_both = " no_lang"
    elif en is True and de is False:
        de_en_both = " single en"
    elif en is False and de is True:
        de_en_both = " single de"
    elif en is True and de is True:
        de_en_both = " de_en_both"

    path_str = f"{total_multi_streams}— {de_en_both}/{path_str}"

    path_str = path_str.replace("Dolby Digital Plus", "DDP")
    path_str = path_str.replace("Dolby Digital", "DD")
    path_str = path_str.replace("MLP FBA Dolby TrueHD", "TrueHD")
    path_str = path_str.replace("TrueHD with Dolby Atmos", "TrueHD & Atmos")
    path_str = path_str.replace("DTS-HD Master Audio", "DTS-HD MA")
    path_str = path_str.replace("DTS-HD High Resolution Audio", "DTS-HD HR")
    path_str = path_str.replace("AC-3 DD", "AC-3")

    print(f"{path_str=}")
    p = pathlib.Path(path_str)
    print(f"{p=}")

    try:
        p.mkdir(parents=True, exist_ok=True)
        print(path)
        path.rename(p / path)
        pathlib.Path(str(path).replace(".mkv", ".png")).rename(p / str(path).replace(".mkv", ".png"))
        pathlib.Path(str(path).replace(".mp4", ".png")).rename(p / str(path).replace(".mp4", ".png"))
    except:
        # filename too long, ignore
        pass


if __name__ == "__main__":
    parser = TArgumentParser(description='sorts video files into folders according to their audio track types and counts')

    args = parser.parse_args()
    # args.paths: List[str]
    paths = args.paths

    for path in paths:
        if str(path) in ["*.mkv", "*.mp4", "*.png"]:
            continue
        print(path)
        main(path)
