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
        delay_str = ""
        if d.get('delay_relative_to_video', 0) > 0:
            delay_str = f", d={d.get('delay_relative_to_video')}"

        format_commercial_name = d.get('commercial_name')
        format = d.get('format', format_commercial_name)
        if format != format_commercial_name:
            if format in format_commercial_name:
                format = format_commercial_name
            elif format_commercial_name in format:
                pass
            else:
                format += " " + format_commercial_name

        langs_dict[d.get('language', "und")].append(f"ch: {d.get('channel_s')}, f={format}{delay_str}")
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
        print()

    items = []
    for k, v in langs_dict.items():
        print(k, len(v))
        if True or len(v) > 1 or k == "und":  # or "d=" in v[0]:
            items.append(f"{k}:{len(v)}{v}")

    print(items)
    if len(items) == 0:
        s = "single"
    else:
        s = ", ".join(sorted(items))
    print(f"{s=}")
    p = pathlib.Path(s)
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
        main(path)
