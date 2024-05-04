#!/usr/bin/env python3

import pathlib
from collections import defaultdict
from typing import List

from pymediainfo import MediaInfo
from tap import Tap


class TArgumentParser(Tap):
    paths: List[pathlib.Path]  # path(s) to file(s)

    def configure(self):
        self.add_argument('paths', nargs="+")


def main(path: pathlib.Path):
    media_info = MediaInfo.parse(path)

    langs_dict = defaultdict(list)

    for a_track in media_info.audio_tracks:
        d = a_track.to_data()

        format_commercial_name = d.get('commercial_name')
        format = d.get('format', format_commercial_name)
        if format != format_commercial_name:
            if format in format_commercial_name:
                format = format_commercial_name
            elif format_commercial_name in format:
                pass
            else:
                format += " " + format_commercial_name

        langs_dict[d.get('language', "und")].append(f"{d.get('channel_s')}×{format}")
        # print(f"{d.get('title')=}")
        # print(f"{d.get('language')=}")
        # print(f"{d.get('channel_s')=}")
        # print(f"{d.get('delay')=}")
        # print(f"{d.get('delay_relative_to_video')=}")
        # print(f"{d.get('codec_id')=}")
        # print(f"{d.get('commercial_name')=}")
        # print(f"{d.get('format')=}")
        # print(f"{d.get('format_info')=}")
        # # pprint.pprint(d)
        # print()

    items_multi = []
    items_single = []
    total_multi_streams = 0
    total_single_streams = 0
    de = False
    en = False
    for lang_code, stream_type in langs_dict.items():
        print(lang_code, len(stream_type))
        de = lang_code == "de" or de
        en = lang_code == "en" or en
        if len(stream_type) > 1 or lang_code == "und":  # or "d=" in v[0]:
            total_multi_streams += len(stream_type)
            items_multi.append(f"{len(stream_type)}×{lang_code}[{', '.join(stream_type)}]")
        elif len(stream_type) <= 1 or lang_code == "und":
            total_single_streams += len(stream_type)
            items_single.append(f"{len(stream_type)}×{lang_code}[{', '.join(stream_type)}]")

    path_str = ""

    print(items_multi)
    print(items_single)

    path_str += ", ".join(sorted(items_multi) + sorted(items_single))

    if en is False and de is False:
        path_str += " no_lang"
    elif en is True and de is False:
        path_str += " single en"
    elif en is False and de is True:
        path_str += " single de"
    elif en is True and de is True:
        path_str += " de_en_both"

    path_str = f"{total_multi_streams}— " + path_str

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
        p.mkdir(exist_ok=True)
        print(path)
        path.rename(p / path)
        path.rename(p / str(path).replace(".mkv", ".png"))
        path.rename(p / str(path).replace(".mp4", ".png"))
    except:
        # filename too long, ignore
        pass

if __name__ == "__main__":
    parser = TArgumentParser(description='sorts video files into folders according to their audio track types and counts')

    args = parser.parse_args()
    args.paths: List[str]
    paths = args.paths

    for path in paths:
        print(path)
        main(path)
