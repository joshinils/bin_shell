#!/usr/bin/env python3

import argparse
import multiprocessing as mp
import pathlib
import subprocess
import traceback
from inspect import currentframe, getframeinfo
from typing import Final, List, Optional, Tuple

import tqdm

normalized_temp_single: Final[pathlib.Path] = pathlib.Path("normalized_temp_single")  # single extracted audio
normalized_temp: Final[pathlib.Path] = pathlib.Path("normalized_temp")  # single normalized audio
normalized_output: Final[pathlib.Path] = pathlib.Path("normalized")  # finished combined file
normalized_done: Final[pathlib.Path] = pathlib.Path("normalized_done")  # original file, not to be deleted


def print_lineno() -> str:
    cf = currentframe()
    return f"{getframeinfo(cf).filename}:{cf.f_back.f_lineno}"


def get_amount_of_audio_streams(path: pathlib.Path) -> Optional[int]:
    commands = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', f"{path}"]
    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
        return len(sub_process_std_out.rstrip().split("\n"))
    except Exception as e:
        print(print_lineno(), type(e), e)
        return None


def extract_audio_stream(path_number: Tuple[pathlib.Path, int]) -> pathlib.Path:
    path = path_number[0]
    stream_number = path_number[1]
    normalized_temp_single.mkdir(exist_ok=True)
    out_name: pathlib.Path = pathlib.Path(f"{normalized_temp_single / path.name}.audio-{stream_number:03}.mkv")
    overwrite = "-n" if no_overwrite_intermediary else "-y"

    commands = ["ffmpeg", "-hide_banner", overwrite, "-i", f"{path}", "-map", f"0:a:{stream_number}", "-c", "copy", f"{out_name}"]
    print("    ", commands)
    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if(sub_process_result.returncode == 0
            or sub_process_result.returncode == 1 and no_overwrite_intermediary
           ):
            return out_name
        else:
            print(print_lineno(), f"{sub_process_result.returncode=}")
            sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_out=}")
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_err=}")
            exit(3)
    except Exception as e:
        print(print_lineno(), type(e), e)
        exit(2)


def get_codec(path: pathlib.Path) -> str:
    global override_codec
    if override_codec is not None:
        return override_codec

    commands = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", f"{path}"]

    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
        sub_process_std_out = sub_process_std_out.strip()
        if sub_process_result.returncode == 0:
            return sub_process_std_out
        else:
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_err=}")
            print(print_lineno(), f"{sub_process_result.returncode=}")
            exit(3)
    except Exception as e:
        print(print_lineno(), type(e), e)
        exit(2)


def get_sample_rate(path: pathlib.Path) -> str:
    if override_codec == "opus":
        return "48000"  # best for opus, can not be something else

    commands = ["ffprobe", "-v", "error", "-select_streams", "a", "-of", "default=noprint_wrappers=1:nokey=1", "-show_entries", "stream=sample_rate", f"{path}"]

    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
        sub_process_std_out = sub_process_std_out.strip()
        if sub_process_result.returncode == 0:
            return sub_process_std_out
        else:
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_err=}")
            print(print_lineno(), f"{sub_process_result.returncode=}")
            exit(3)
    except Exception as e:
        print(print_lineno(), type(e), e)
        exit(2)


def get_channel_count(path: pathlib.Path) -> int:
    commands = ["ffprobe", "-show_entries", "stream=channels", "-of", "compact=p=0:nk=1", "-v", "0", f"{path}"]
    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
        sub_process_std_out = sub_process_std_out.strip()
        if sub_process_result.returncode == 0:
            return int(sub_process_std_out)
        else:
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_err=}")
            print(print_lineno(), f"{sub_process_result.returncode=}")
            exit(3)
    except Exception as e:
        print(print_lineno(), type(e), e)
        exit(2)


def normalize(path: pathlib.Path) -> pathlib.Path:
    out_name: pathlib.Path = pathlib.Path(f"{normalized_temp / path.name}.normalized.mkv")
    if no_overwrite_intermediary and out_name.is_file():
        path.unlink()  # remove old single extracted audio file
        return out_name
        # TODO add codec to filename
        # TODO add samplerate to filename

    codec = get_codec(path)
    sample_rate = get_sample_rate(path)

    bitrate_list = []
    bitrate_lut = {
        2: 128_000,
        6: 320_000,
        8: 448_000
    }
    if not ignore_bitrate:
        num_channels = get_channel_count(path)
        audio_bitrate = bitrate_lut[num_channels]
        bitrate_list = ["-b:a", f"{audio_bitrate}"]

    commands = ["ffmpeg-normalize", "-pr", "-f", "-ar", f"{sample_rate}", "-c:a", codec] + bitrate_list + [f"{path}", "-o", f"{out_name}", "-e", "-strict -2"]
    print("    ", commands)
    try:
        logfile_name = pathlib.Path(path.name + ".log")
        with open(logfile_name, "w") as logfile:
            normalized_temp.mkdir(exist_ok=True)
            sub_process_result = subprocess.run(
                commands,
                stdout=logfile,
                stderr=logfile
            )
        if sub_process_result.returncode == 0:
            path.unlink()  # remove old single extracted audio file
            logfile_name.unlink()  # remove logfile, everything went ok
            return out_name
        else:
            print(print_lineno(), f"{sub_process_result.returncode=}", f"""see logfile: "{logfile_name=}" """)
            exit(3)
    except Exception as e:
        print(print_lineno(), type(e), e)
        exit(2)


def extract_and_normalize_single_audio_stream(path_number: Tuple[pathlib.Path, int]) -> pathlib.Path:
    audio_path = extract_audio_stream(path_number)
    normalized_path = normalize(audio_path)
    return normalized_path


def extract_and_normalize(path: pathlib.Path) -> List[pathlib.Path]:
    audio_stream_count = get_amount_of_audio_streams(path)
    with mp.Pool(processes=audio_stream_count) as mp_pool:
        tasks = []
        for audio_stream in range(audio_stream_count):
            tasks.append((path, audio_stream))
        result_paths: List[pathlib.Path] = list(tqdm.tqdm(mp_pool.imap_unordered(extract_and_normalize_single_audio_stream, tasks), total=audio_stream_count, desc="extract and normalize"))
        result_paths.sort()
        # mp_pool.close()
        # mp_pool.join()

    return result_paths


def merge_normalized_with_video_subs(video_path: pathlib.Path, normalized_audio: List[pathlib.Path]) -> None:
    video_path_name = video_path.name
    if override_codec != "opus":
        name_parts = video_path.name.split(".")
        last_part = name_parts.pop()
        video_path_name = f"""{".".join(name_parts)} ({override_codec}).{last_part}"""
    out_name = normalized_output / video_path_name

    normalized_output.mkdir(exist_ok=True)

    commands = ["mkvmerge", "-v", "-o", out_name, "--no-audio", video_path] + normalized_audio
    commands = [str(elem) for elem in commands]
    print("    ", commands)

    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if(sub_process_result.returncode == 0
            or sub_process_result.returncode == 1 and no_overwrite_intermediary
           ):
            normalized_done.mkdir(exist_ok=True)
            video_path.rename(normalized_done / video_path.name)
        else:
            sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_out=}")
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_std_err=}")
            print(print_lineno(), f"{sub_process_result.returncode=}")
            exit(3)
    except Exception as e:
        print(traceback.print_exc())
        print(type(e), e)
        exit(2)

    for path in normalized_audio:
        path.unlink()


global override_codec
override_codec: str

global ignore_bitrate
ignore_bitrate: bool

global no_overwrite_intermediary
no_overwrite_intermediary: bool


def main():
    parser = argparse.ArgumentParser(description='normalizes a movie file, each audio track by itself, encodes to opus with bitrates for channel layouts - 2ch = 128 kb/s, 5.1 = 320 kb/s, 7.1 = 448 kb/s')

    parser.add_argument(
        "path",
        type=pathlib.Path,
        help='path to file',
    )

    parser.add_argument(
        "-c:a",
        "--force_codec",
        required=False,
        type=str,
        default="opus",
        metavar="codec",
        help="default opus, with bitrates for opus",
    )

    parser.add_argument(
        "-nb",
        "--ignore_bitrate",
        action="store_true"
    )

    parser.add_argument(
        "-n",
        "--no_overwrite_intermediary",
        action="store_true"
    )

    args = parser.parse_args()

    path: pathlib.Path = pathlib.Path(args.path)
    if not path.exists():
        print(f"""file "{path}" does not exist""")
        exit(1)

    global override_codec
    override_codec = args.force_codec
    global ignore_bitrate
    ignore_bitrate = args.ignore_bitrate
    global no_overwrite_intermediary
    no_overwrite_intermediary = args.no_overwrite_intermediary

    normalized_audio_paths = extract_and_normalize(path)
    merge_normalized_with_video_subs(video_path=path, normalized_audio=normalized_audio_paths)


if __name__ == "__main__":
    main()
