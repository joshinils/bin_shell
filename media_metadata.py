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

    items = []
    total_multi_streams = 0
    for k, v in langs_dict.items():
        print(k, len(v))
        if len(v) > 1 or k == "und":  # or "d=" in v[0]:
            total_multi_streams += len(v)
            items.append(f"{len(v)}×{k}[{', '.join(v)}]")

    print(items)
    if len(items) == 0:
        path_str = "single"
    else:
        path_str = ", ".join(sorted(items))

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
    p.mkdir(exist_ok=True)
    print(path)
    path.rename(p / path)


if __name__ == "__main__":
    parser = TArgumentParser(description='sorts video files into folders according to their audio track types and counts')

    args = parser.parse_args()
    args.paths: List[str]
    paths = args.paths

    for path in paths:
        print(path)
        main(path)
