#!/usr/bin/env python3

import argparse
import datetime
import json
import multiprocessing as mp
import os
import pathlib
import subprocess
from typing import Any, Dict, List, Tuple, Union

import exif  # https://pypi.org/project/exif/
import tqdm


def read_json(path: pathlib.Path):
    if not path.is_file():
        print(f"The file \"{path}\" does not exist!")
        exit(1)

    d = dict()
    with open(path) as f:
        d: Dict = json.load(f)
    return d


def split_ok_error(json_data) -> Dict[str, List]:
    images: Dict[str, List] = {"no_error": []}

    elem: Dict[str, Union[str, Dict]]
    for elem in json_data:
        if "error" in elem:
            error_type = elem["error"].get("type", "_unknown_error")
            if error_type not in images:
                images[error_type] = []
            images[error_type].append(elem["error"].get("vars", elem["error"]).get("desc", elem["error"]["vars"]))
        else:
            images["no_error"].append(elem)

    return images


def save_with_metadata(path_number: Tuple[str, Dict[str, Union[str, Dict[str, str]]]]) -> int:
    # unpack arguments tuple
    error_type: str
    image_info: Dict[str, Union[str, Dict[str, str]]]
    error_type, image_info = path_number

    necessary_metadata = [
        "filename",
        "MAPLatitude",
        "MAPLongitude",
        "MAPCaptureTime",
    ]
    for key in necessary_metadata:
        if key not in image_info:
            print("skipping image")
            return

    filepath = pathlib.Path(image_info["filename"])
    if not filepath.is_file():
        print(f"The image \"{filepath}\" does not exist!")
        return

    with open(filepath, 'rb') as image:
        my_image = exif.Image(image)

    #                                                              2023_04_30_15_10_17_100
    date = datetime.datetime.strptime(image_info["MAPCaptureTime"], "%Y_%m_%d_%H_%M_%S_%f")
    iso_8601 = date.strftime("%Y:%m:%d %H:%M:%S.%f") + "Z"
    # print(iso_8601)
    my_image.datetime = iso_8601
    my_image.datetime_original = iso_8601
    my_image.subsec_time_original = date.strftime("%f")
    # my_image.gps_timestamp = date.strftime("%H:%M:%S")
    # my_image.gps_datestamp = date.strftime("%Y:%m:%d %H:%M:%S")
    # my_image.gps_latitude = image_info["MAPLatitude"]
    # my_image.gps_longitude = image_info["MAPLongitude"]
    my_image.make = "GoPro"
    my_image.model = "GoPro Max"

    output_path = pathlib.Path(os.getcwd()) / "output" / error_type / filepath.name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as new_image_file:
        new_image_file.write(my_image.get_file())

    # ffs, exiftool package can not set arbitrary tags...
    # make image show as 360° image
    subprocess.run([
        "exiftool",
        "-overwrite_original",
        "-DateTimeOriginal=" + iso_8601,
        "-XMP-GPano:UsePanoramaViewer=True",
        "-XMP-GPano:ProjectionType=equirectangular",
        "-XMP-GPano:CroppedAreaImageWidthPixels=5376",
        "-XMP-GPano:CroppedAreaImageHeightPixels=2688",
        "-XMP-GPano:FullPanoWidthPixels=5376",
        "-XMP-GPano:FullPanoHeightPixels=2688",
        "-XMP-GPano:CroppedAreaTopPixels=0",
        "-XMP-GPano:CroppedAreaLeftPixels=0",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 1  # for progress_bar update callback as argument


def main(path: pathlib.Path, max_threads: int, chunksize: int) -> None:
    json_data = read_json(path)
    images = split_ok_error(json_data)

    progress_bar = tqdm.tqdm(dynamic_ncols=True)
    progress_bar.total = 0
    description_length = 0
    for key in images:
        progress_bar.total += len(images[key])
        description_length = max(description_length, len(key))
    progress_bar.refresh()

    tasks: List[Tuple[str, Dict[str, Union[str, Dict[str, str]]]]] = list()
    for error_type, elem_lst in images.items():
        image_info: Union[Dict, Any]
        for image_info in elem_lst:
            tasks.append((error_type, image_info))

    with mp.Pool(processes=max_threads) as mp_pool:
        results = mp_pool.imap_unordered(save_with_metadata, tasks, chunksize=chunksize)
        mp_pool.close()
        for elem in results:
            progress_bar.update(elem)
        mp_pool.join()

    progress_bar.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='uses metadata from json file and writes to therein referenced images exif')

    parser.add_argument(
        "json_file",
        type=pathlib.Path,
        help='path to json file containing mapillary_tool metadata',
        metavar="path",
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        help='threads to use at the same time',
        metavar="num",
        required=False,
        default=8,
    )

    parser.add_argument(
        "-c",
        "--chunksize",
        type=int,
        help='chunksize to use per thread',
        metavar="num",
        required=False,
        default=8,
    )

    args = parser.parse_args()

    json_path: pathlib.Path = pathlib.Path(args.json_file)
    max_threads: int = args.threads
    chunksize: int = args.chunksize
    main(json_path, max_threads, chunksize)
