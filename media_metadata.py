#!/usr/bin/env python3

import json
import pathlib
import subprocess
import sys
from collections import defaultdict
from typing import List

from tap import Tap


def eprint(*args, **kwargs) -> None:  # type: ignore
    print(*args, file=sys.stderr, **kwargs)


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
    keepsies = dict()
    for elem in metadata_json:
        if elem.get("type") != "audio":
            continue
        # print(type(elem), elem)

        flag_visual_impaired = elem.get("properties", {}).get("flag_visual_impaired")
        flag_commentary = elem.get("properties", {}).get("flag_commentary")
        lang_code = elem.get("properties", {"language_ietf": "und"}).get("language_ietf", "und")
        channel_count = elem.get("properties", {"audio_channels": 0}).get("audio_channels", 0)

        if lang_code == "und":
            lang_code = elem.get("properties", {"language": "und"}).get("language", "und")
            lang_dict = {  # ISO-639-2 -> ISO-639-1
                "ger": "de",
                "eng": "en",
                "fre": "fr",
                "jpn": "jp",
                "ita": "it",
                "spa": "es",
                "por": "pt",
                "pol": "pl",
                "rus": "ru",
                "tha": "th",
                "tur": "tr",
                "chi": "zh",
                "dut": "nl",
                "fin": "fi",
                "swe": "sv",
                "hun": "hu",
                "cze": "cs",
                "dan": "da",
                "cat": "ca",
                "rum": "ro",
                "ukr": "uk",
                "kor": "ko",
                "heb": "he",
                "nor": "no",
                "hin": "hi",
                "gre": "el",
                "ice": "is",
                "ind": "id",
                "und": "und",
            }
            if lang_code in lang_dict:
                lang_code = lang_dict.get(lang_code, lang_code)
            else:
                eprint(f"{lang_code=} found, not sure what to do with it.")

        if flag_commentary:
            lang_code += "-co"
        if flag_visual_impaired:
            lang_code += "-vi"
        lang_code += f"*{channel_count}"

        # print(f"{flag_commentary=} {flag_visual_impaired=} {language=} {format=}")

        stream_format = elem.get("codec")
        keepsies[elem["id"] - 1] = lang_code, stream_format

        print(f"{stream_format=}")
        langs_dict[lang_code].append(f"{stream_format}")
        print()

    # print(f"{keepsies=}")

    items_multi_to_generate_spectograms = set()
    items_multi = []
    items_single = []
    total_multi_streams = 0
    total_single_streams = 0
    de = False
    en = False
    for lang_code, stream_formats_list in langs_dict.items():
        print(lang_code, len(stream_formats_list))
        de = lang_code.split("*")[0] == "de" or de
        en = lang_code.split("*")[0] == "en" or en
        if len(stream_formats_list) > 1 or lang_code == "und":  # or "d=" in v[0]:
            items_multi.append(f"{len(stream_formats_list)}×{lang_code}[{', '.join(stream_formats_list)}]")
            for index, lang_code__stream_format in keepsies.items():
                for stream_format__ in stream_formats_list:
                    print(f"{lang_code=} {stream_format__=}  {lang_code__stream_format=}")
                    if lang_code__stream_format == (lang_code, stream_format__):
                        items_multi_to_generate_spectograms.add((index, lang_code, stream_format__))
            if "-co" in lang_code:
                continue
            total_multi_streams += len(stream_formats_list)
        elif len(stream_formats_list) <= 1 or lang_code == "und":
            items_single.append(f"{len(stream_formats_list)}×{lang_code}[{', '.join(stream_formats_list)}]")
            total_single_streams += len(stream_formats_list)

    print(f"{items_multi_to_generate_spectograms=}")

    path_str = ""

    print(f"{items_multi=}")
    print(f"{items_single=}")

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

    path_str = path_str.replace("Dolby Digital Plus", "DDP")
    path_str = path_str.replace("Dolby Digital", "DD")
    path_str = path_str.replace("MLP FBA Dolby TrueHD", "TrueHD")
    path_str = path_str.replace("TrueHD with Dolby Atmos", "TrueHD & Atmos")
    path_str = path_str.replace("DTS-HD Master Audio", "DTS-HD MA")
    path_str = path_str.replace("DTS-HD High Resolution Audio", "DTS-HD HR")
    path_str = path_str.replace("AC-3 DD", "AC-3")
    path_str = path_str.replace("/", "∕")  # sanity, don't create subdirs willy nilly!

    path_str = f"{total_multi_streams}— {de_en_both}/{path_str}"

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

    # generate spectograms in the new folder
    # bash example: ffmpeg -hide_banner -loglevel warning -t 30 -i "$1" -filter_complex "[0:a:${2}]showspectrumpic=2276x1312:mode=combined:scale=log:color=channel:win_func=gauss:saturation=-2:gain=2" -n "${1// /_}_s${2// /_}_${language}_spectrum.png"
    for stream_index, lang_code, stream_format in items_multi_to_generate_spectograms:
        print(f"{stream_index=} {lang_code=} {stream_format=}")
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-t",
            "300",
            "-i",
            str(p / path),
            "-filter_complex",
            f"[0:a:{stream_index}]showspectrumpic=2276x1312:mode=combined:scale=log:color=channel:win_func=gauss:saturation=-2:gain=2",
            "-n",
            str(p / f"{path.stem}_s{stream_index}_{lang_code}_{stream_format}_spectrum.png".replace("/", "∕")),
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
            print(f"spectrogram subprocess {result=}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing ffmpeg: {e}")
            raise Exception


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
