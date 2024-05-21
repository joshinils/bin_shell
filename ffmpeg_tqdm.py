#!/usr/bin/env python3

from tqdm import tqdm
import ffmpeg_progress_yield
import sys

with tqdm(
    total=100,
    position=1,
    desc="Running Command",
) as pbar:
    for progress in ffmpeg_progress_yield.FfmpegProgress(["ffmpeg"] + sys.argv[1:]).run_command_with_progress():
        pbar.update(progress - pbar.n)

