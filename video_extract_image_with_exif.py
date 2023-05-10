#!/usr/bin/env python3

import pathlib

import cv2
import exif

from python_funs.video import (
    extract_frame, get_duration, get_frame_at, get_framerate, get_frames,
    get_width
)


def extract_images():
    "ffmpeg -i GS015642.mov -vsync 0 -frame_pts true -metadata output_folder/output_%03d.jpg"


def main() -> None:
    path = pathlib.Path('GS015642.mov')

    # fps = get_framerate(path)
    # duration = get_duration(path)
    frame = extract_frame(path, 42)
    exit()

    vidcap = cv2.VideoCapture(path)

    success, image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite(f"frame{count:03g}.jpg", image)     # save frame as JPEG file
        success, image = vidcap.read()
        print('Read a new frame: ', success, count)
        count += 1

    exit()

    with open("filename.jpg", 'rb') as image:
        my_image = exif.Image(image)
    print(my_image.has_exif)
    print(my_image.list_all())

    my_image.datetime_original = "2023-04-30 01:23:45+02:00"

    print(my_image.has_exif)
    print(my_image.list_all())

    with open('modified_image.jpg', 'wb') as new_image_file:
        new_image_file.write(my_image.get_file())


if __name__ == "__main__":
    main()
