#!/usr/bin/env python3

import argparse
import multiprocessing as mp
import pathlib
import subprocess
import traceback
from inspect import currentframe, getframeinfo
from typing import Dict, Final, List, Optional, Tuple, TypedDict

import tqdm

normalized_temp_single: Final[pathlib.Path] = pathlib.Path("normalized_temp_single")  # single extracted audio
normalized_temp: Final[pathlib.Path] = pathlib.Path("normalized_temp")  # single normalized audio
normalized_staging: Final[pathlib.Path] = pathlib.Path("normalized_staging")  # compile combined file here
normalized_output: Final[pathlib.Path] = pathlib.Path("normalized")  # finished combined file
normalized_done: Final[pathlib.Path] = pathlib.Path("normalized_done")  # original file, not to be deleted


class NameInfo(TypedDict):
    done: List[pathlib.Path]
    count: int


def print_lineno() -> str:
    cf = currentframe()
    return f"{getframeinfo(cf).filename}:{cf.f_back.f_lineno}"


def rmdir(path: pathlib.Path) -> None:
    # remove directory, iff empty
    commands = ['rmdir', '--ignore-fail-on-non-empty', '-p', f"{path}"]
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


def get_amount_of_audio_streams(path: pathlib.Path) -> Optional[int]:
    commands = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', f"{path}"]
    try:
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
        if sub_process_std_out.rstrip() == "":
            return 0
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
    if override_codec == "libopus":
        return "48000"  # best for libopus, can not be something else

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
    logfile_name = pathlib.Path(path.name + ".log")
    if no_overwrite_intermediary and out_name.is_file():
        path.unlink()  # remove old single extracted audio file
        logfile_name.unlink(missing_ok=True)
        return out_name
        # TODO add codec to filename
        # TODO add samplerate to filename

    codec = get_codec(path)
    sample_rate = get_sample_rate(path)

    bitrate_list = []
    bitrate_lut = {
        1:  64_000,  # noqa: E241  # mono
        2: 128_000,  # stereo
        5: 192_000,  # 4.1, Alien 1978, 5-kanal
        6: 320_000,  # 5.1
        7: 384_000,  # 6.1
        8: 448_000,  # 7.1
    }

    num_channels = get_channel_count(path)
    if not ignore_bitrate:
        audio_bitrate = bitrate_lut[num_channels]
        bitrate_list = ["-b:a", f"{audio_bitrate}"]

    commands = ["ffmpeg-normalize", "-pr", "-f", "-ar", f"{sample_rate}", "-c:a", codec] + bitrate_list + [f"{path}", "-o", f"{out_name}", "-e", f"-ac {num_channels} -dsurex_mode 1"]
    print("    ", commands)
    try:
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
            rmdir(normalized_temp_single)
            return out_name
        else:
            print(print_lineno(), f"{sub_process_result.returncode=}", f"""see logfile: "{logfile_name=}" """)
            exit(3)
    except Exception as e:
        print(print_lineno(), type(e), e)
        exit(2)


def make_lockfile_name(path: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(str(path) + ".working")


def extract_and_normalize_single_audio_stream(path_number: Tuple[pathlib.Path, int]) -> Tuple[Optional[pathlib.Path], Optional[pathlib.Path]]:
    if not path_number[0].exists():
        return (None, None)

    with open(make_lockfile_name(path_number[0]), "w"):
        pass
    audio_path = extract_audio_stream(path_number)
    if extract_only:
        return (None, None)
    normalized_path = normalize(audio_path)
    return (normalized_path, path_number[0])


def mkvmerge_normalized_with_video_subs(video_path: pathlib.Path, normalized_audio: List[pathlib.Path]) -> None:
    video_out_name = video_path.name
    if override_codec != "libopus":
        name_parts = video_path.name.split(".")
        last_part = name_parts.pop()
        video_out_name = f"""{".".join(name_parts)} ({override_codec}).{last_part}"""

    out_name = normalized_staging / video_out_name

    commands = ["mkvmerge", "-v", "-o", out_name, "--no-audio", video_path] + normalized_audio
    commands = [str(elem) for elem in commands]
    print("    ", commands)

    try:
        normalized_staging.mkdir(exist_ok=True)
        sub_process_result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        status_ok = sub_process_result.returncode == 0
        warning = sub_process_result.returncode == 1
        error = sub_process_result.returncode != 0 and sub_process_result.returncode != 1

        if status_ok or warning:
            normalized_done.mkdir(exist_ok=True)
            video_path.rename(normalized_done / video_path.name)

            normalized_output.mkdir(exist_ok=True)
            out_name.rename(normalized_output / video_out_name)
            rmdir(normalized_staging)
        if not status_ok:
            sub_process_std_out = sub_process_result.stdout.decode('utf-8', errors="ignore")
            sub_process_std_err = sub_process_result.stderr.decode('utf-8', errors="ignore")
            print(print_lineno(), f"{sub_process_result.returncode=}")

            if warning:
                sub_process_std_err = sub_process_std_err.replace("\\n", "warning:    \n")
                sub_process_std_out = sub_process_std_out.replace("\\n", "warning:    \n")
                print(print_lineno(), f"\nwarning:    {sub_process_std_out=}")
                print(print_lineno(), f"\nwarning:    {sub_process_std_err=}")

            if error:
                print(print_lineno(), f"{sub_process_std_out=}")
                print(print_lineno(), f"{sub_process_std_err=}")
                exit(3)
    except Exception as e:
        print(traceback.print_exc())
        print(type(e), e)
        exit(2)

    for path in normalized_audio:
        path.unlink()
    rmdir(normalized_temp_single)
    rmdir(normalized_staging)

    make_lockfile_name(video_path).unlink()


def extract_normalize_merge_all(paths: List[pathlib.Path]) -> None:
    path_streams = []
    for path in paths:
        if skip_dot_working and make_lockfile_name(path).is_file():
            continue
        path_streams.append((path, get_amount_of_audio_streams(path), path.stat().st_size))

    path_streams.sort(key=lambda x: x[2], reverse=True)
    path_streams.sort(key=lambda x: x[1], reverse=True)

    dict_orig_normed_counts: Dict[pathlib.Path, NameInfo] = dict()
    tasks: List[Tuple[pathlib.Path, int]] = list()
    for path, audio_stream_count, _ in path_streams:
        dict_orig_normed_counts[path] = {"done": [], "count": audio_stream_count}
        for audio_stream in range(audio_stream_count):
            tasks.append((path, audio_stream))

    with mp.Pool() as mp_pool_merge:
        with mp.Pool(processes=max_threads) as mp_pool_extract_norm:
            results = mp_pool_extract_norm.imap_unordered(extract_and_normalize_single_audio_stream, tasks)
            mp_pool_extract_norm.close()

            for path_normalized, path_orig in tqdm.tqdm(results, total=len(tasks), dynamic_ncols=True, desc="extract, norm, merge"):
                if path_normalized is None or path_orig is None:
                    continue
                dict_orig_normed_counts[path_orig]["done"].append(path_normalized)
                if len(dict_orig_normed_counts[path_orig]["done"]) >= dict_orig_normed_counts[path_orig]["count"]:
                    mp_pool_merge.apply_async(mkvmerge_normalized_with_video_subs, kwds={"video_path": path_orig, "normalized_audio": dict_orig_normed_counts[path_orig]["done"]})
                    del dict_orig_normed_counts[path_orig]
            mp_pool_merge.close()
            mp_pool_extract_norm.join()
        mp_pool_merge.join()


global override_codec
override_codec: str

global ignore_bitrate
ignore_bitrate: bool

global no_overwrite_intermediary
no_overwrite_intermediary: bool

global max_threads
max_threads: int

global skip_dot_working
skip_dot_working: bool

global extract_only
extract_only: bool


def main():
    parser = argparse.ArgumentParser(description='normalizes a movie file, each audio track by itself, encodes to libopus with bitrates for channel layouts - 2ch = 128 kb/s, 5.1 = 320 kb/s, 7.1 = 448 kb/s')

    parser.add_argument(
        "paths",
        type=pathlib.Path,
        help='path(s) to file(s)',
        metavar="path1 [path2 ...]",
        nargs="+",
    )

    parser.add_argument(
        "-c:a",
        "--force_codec",
        required=False,
        type=str,
        default="libopus",
        metavar="codec",
        help="default libopus, with bitrates for libopus",
    )

    parser.add_argument(
        "-t",
        "--max_threads",
        required=False,
        type=int,
        default=4,
        metavar="thread_count",
        help="default 4, threads to use",
    )

    parser.add_argument(
        "-nb",
        "--ignore_bitrate",
        action="store_true",
    )

    parser.add_argument(
        "-n",
        "--no_overwrite_intermediary",
        action="store_true",
    )

    parser.add_argument(
        "-w",
        "--skip_dot_working",
        action="store_true",
        help="skip, if a *.working file exists",
    )

    parser.add_argument(
        "-x",
        "--extract_only",
        action="store_true",
        help="exit after extracting audio",
    )

    args = parser.parse_args()

    input_paths: List[pathlib.Path] = [pathlib.Path(p) for p in args.paths]
    paths = []
    for pot_path in input_paths:
        if not pot_path.exists():
            print(f"""file "{pot_path}" does not exist, ignoring file""")
        else:
            paths.append(pot_path)

    if len(paths) == 0:
        print("no existing paths give, exiting")
        exit(1)

    global override_codec
    override_codec = args.force_codec

    global ignore_bitrate
    ignore_bitrate = args.ignore_bitrate

    global no_overwrite_intermediary
    no_overwrite_intermediary = args.no_overwrite_intermediary

    global max_threads
    max_threads = args.max_threads

    global skip_dot_working
    skip_dot_working = args.skip_dot_working

    global extract_only
    extract_only = args.extract_only

    rmdir(normalized_temp_single)
    rmdir(normalized_staging)
    rmdir(normalized_output)
    rmdir(normalized_done)

    extract_normalize_merge_all(paths)


if __name__ == "__main__":
    main()
