#!/usr/bin/env python3

import argparse
import multiprocessing as mp
import pathlib
import subprocess
from typing import List, Optional, Tuple

import tqdm


def get_amount_of_audio_streams(path: pathlib.Path) -> Optional[int]:
    try:
        sub_process_result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', path],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
        return len(sub_process_std_out.rstrip().split("\n"))
    except Exception as e:
        print(e)
        return None


def extract_single_audio_stream(path_number: Tuple[pathlib.Path, int]) -> pathlib.Path:
    path = path_number[0]
    stream_number = path_number[1]
    try:
        out_name = f"{path}.audio-{stream_number:03}.mkv"
        sub_process_result = subprocess.run(["ffmpeg", "-i", path, "-map", f"0:a:{stream_number}", "-c", "copy", out_name, "-y"],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        if(sub_process_result.returncode) == 0:
            return out_name
        else:
            sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
            print(sub_process_std_out)
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(sub_process_std_err)
            exit(3)
    except Exception as e:
        print(e)
        exit(2)


def extract_audio_streams(path: pathlib.Path) -> List[pathlib.Path]:
    audio_stream_count = get_amount_of_audio_streams(path)
    with mp.Pool(processes=audio_stream_count) as mp_pool:
        tasks = []
        for audio_stream in range(audio_stream_count):
            tasks.append((path, audio_stream))
        result_paths: List[pathlib.Path] = list(tqdm.tqdm(mp_pool.imap_unordered(extract_single_audio_stream, tasks), total=audio_stream_count))
        result_paths.sort()
        # mp_pool.close()
        # mp_pool.join()

    return result_paths


def main():
    parser = argparse.ArgumentParser(description='normalizes a movie file, each audio track by itself')

    parser.add_argument(
        "path",
        type=pathlib.Path,
        help='path to file',
    )
    args = parser.parse_args()
    path: pathlib.Path = args.path
    if not path.exists():
        print(f"""file "{path}" does not exist""")
        exit(1)
    audio_paths = extract_audio_streams(path)
    print(audio_paths)


if __name__ == "__main__":
    main()
