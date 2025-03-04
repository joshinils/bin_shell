#!/usr/bin/python3

import argparse
import math
import os
import pathlib
import statistics
import subprocess
from typing import Optional

import numpy as np
from PIL import Image

from normalize import get_amount_of_audio_streams
from python_funs.video import get_duration


def gen_diff_buffer(
    image1_path: pathlib.Path,
    image2_path: pathlib.Path
) -> Optional[Image.Image]:
    if not image1_path.exists():
        print(f'{image1_path} does not exist')
        return None

    if not image2_path.exists():
        print(f'{image2_path} does not exist')
        return None

    if image1_path.is_dir():
        print(f'{image1_path} is a directory')
        return None

    if image2_path.is_dir():
        print(f'{image2_path} is a directory')
        return None

    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    if image1.size != image2.size:
        print('Images are different sizes')
        return None

    buffer1 = np.asarray(image1, dtype=np.int32)
    buffer2 = np.asarray(image2, dtype=np.int32)

    buffer_diff = buffer1 - buffer2
    return buffer_diff


def gen_diff_image(
    image1_path: pathlib.Path,
    image2_path: pathlib.Path
) -> Optional[Image.Image]:
    buffer_diff = gen_diff_buffer(image1_path, image2_path)

    if buffer_diff is None:
        return None

    median = statistics.median(buffer_diff)
    mean = statistics.mean(buffer_diff)
    min_val = np.min(buffer_diff)
    max_val = np.max(buffer_diff)

    print(f"Median: {median}, Mean: {mean}, Min: {min_val}, Max: {max_val}")

    # change type of buffer_diff back to uint8
    buffer_diff = np.asarray(abs(buffer_diff), dtype=np.uint8)

    image_diff = Image.fromarray(buffer_diff, 'RGB')
    return image_diff


def gen_spectogram(
    media_path: pathlib.Path,
    stream_index: int,
    start_time: float,
    duration: float = 300,
    differentiator: str = "",
) -> Optional[pathlib.Path]:
    # bash example: ffmpeg -hide_banner -loglevel warning -t 30 -i "$1" -filter_complex "[0:a:${2}]showspectrumpic=2276x1312:mode=combined:scale=log:color=channel:win_func=gauss:saturation=-2:gain=2" -n "${1// /_}_s${2// /_}_${language}_spectrum.png"

    if not media_path.exists():
        print(f'{media_path} does not exist')
        return None

    if media_path.is_dir():
        print(f'{media_path} is a directory')
        return None

    out_path = pathlib.Path(f"{media_path.stem}_{differentiator}_s{stream_index}_spectrum.png")

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-ss",
        str(start_time),
        "-t",
        str(duration),
        "-i",
        str(media_path),
        "-filter_complex",
        f"[0:a:{stream_index}]showspectrumpic=2560x1440:mode=combined:scale=log:color=channel:win_func=gauss:saturation=-2:gain=2:legend=off",
        "-n",
        str(out_path),
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        print(f"spectogram subprocess {result=}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing ffmpeg: {e}")
        raise Exception
    return out_path


def gen_diff_image_from_media_single(
    fileA_path: pathlib.Path,
    fileB_path: pathlib.Path,
    stream_index: int,
    start_time: float = 0,
    duration: float = 300
) -> Optional[str]:
    if fileA_path.stem == fileB_path.stem:
        differentiatorA = "A"
        differentiatorB = "B"
    else:
        differentiatorA = ""
        differentiatorB = ""

    spec_a = gen_spectogram(fileA_path, stream_index, start_time, duration, differentiatorA)
    if spec_a is None:
        print(f"Failed to generate spectogram for {fileA_path}")
        return None

    spec_b = gen_spectogram(fileB_path, stream_index, start_time, duration, differentiatorB)
    if spec_b is None:
        print(f"Failed to generate spectogram for {fileB_path}")
        return None

    image_diff = gen_diff_image(spec_a, spec_b)
    if image_diff is None:
        print("Failed to generate difference image.")
        return None

    common_stem = os.path.commonprefix([fileA_path.stem, fileB_path.stem])
    postfixes = set([
        fileA_path.stem.replace(common_stem, ''),
        fileB_path.stem.replace(common_stem, '')
    ])
    postfixes.discard('original')
    common_stem = common_stem.removesuffix('_')

    out_name = f"{common_stem}_{'_'.join(postfixes)}_s{stream_index:>03}_diff.png"
    image_diff.save(out_name)

    spec_a.unlink()
    spec_b.unlink()

    return out_name


def main() -> None:
    argparser = argparse.ArgumentParser(
        description='Diff two media files audio spectograms'
    )
    argparser.add_argument('fileA', help='First media file')
    argparser.add_argument('fileB', help='second media file')

    args = argparser.parse_args()
    fileA_path = pathlib.Path(args.fileA)
    fileB_path = pathlib.Path(args.fileB)

    duration_A = get_duration(fileA_path)
    duration_B = get_duration(fileB_path)

    duration = min(duration_A, duration_B)
    spectogram_duration = 300.0  # 5 minutes
    credits_offset = duration * 8 / 120 if duration > spectogram_duration * 2 else 0
    start_time = math.floor(duration - spectogram_duration - credits_offset)

    if start_time <= 0:
        start_time = 0
        spectogram_duration = min(duration, spectogram_duration)

    audio_count_A = get_amount_of_audio_streams(fileA_path)
    audio_count_B = get_amount_of_audio_streams(fileB_path)

    if audio_count_A != audio_count_B:
        print(f"Audio streams count mismatch: {audio_count_A} != {audio_count_B}")
        return
    if audio_count_A == 0 or audio_count_A is None:
        print("No audio streams found")
        return

    for stream_index in range(audio_count_A):
        gen_diff_image_from_media_single(fileA_path, fileB_path, stream_index, start_time, spectogram_duration)


if __name__ == '__main__':
    main()
