import pathlib
from typing import Optional

import cv2
import numpy


def get_frame_at(path: pathlib.Path, sec: float):
    vidcap: cv2.VideoCapture = cv2.VideoCapture(str(path))
    vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    hasFrames, image = vidcap.read()
    if hasFrames:
        cv2.imwrite(f"frames/{sec}sec.png", image)
    return hasFrames


def extract_frame(path: pathlib.Path, sec: float) -> Optional[numpy.ndarray]:
    vidcap: cv2.VideoCapture = cv2.VideoCapture(str(path))
    vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    image: numpy.ndarray
    hasFrames, image = vidcap.read()
    if hasFrames:
        return image
    return None


def get_width(path: pathlib.Path) -> int:
    cap = cv2.VideoCapture(str(path))
    if cap.isOpened():
        return int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    return None


def get_frames(path: pathlib.Path) -> int:
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


def get_framerate(path: pathlib.Path) -> float:
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    return cap.get(cv2.CAP_PROP_FPS)


def get_duration(path: pathlib.Path) -> float:
    return get_frames(path) / get_framerate(path)
