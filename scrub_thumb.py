#!/usr/bin/env python3

import sys
import cv2
import numpy as np
import tqdm
from python_funs.video import get_frame_at, extract_frame, get_width, get_frames, get_framerate, get_duration
from collections import defaultdict

def main() -> None:
    path = sys.argv[1]
    width_physical = get_width(path)
    width_output = width_physical
    duration = get_duration(path)


    # width_output = 100

    rows = 2
    width_output *= rows
    width_total_slices = width_output * rows

    compiled = defaultdict(lambda: None)

    bar = tqdm.tqdm(dynamic_ncols=True, total=width_total_slices)
    for index_slice, time in enumerate(np.linspace(0, stop=duration, num=width_total_slices + 1, endpoint=True)[:width_total_slices]):
        index_for_row_counter = index_slice
        row = 0
        while index_for_row_counter >= width_output:
            index_for_row_counter -= width_output
            row += 1

        index_physical = index_slice // (rows ** 2)

        bar.write(f"{index_slice=}, {index_physical=}, {row=}, {time=}")
        frame = extract_frame(path, time)
        if frame is None:
            continue
        slice = frame[:, index_physical:index_physical + 1]
        if compiled[row] is None:
            compiled[row] = slice
        else:
            compiled[row] = np.hstack((compiled[row], slice))
        bar.update()
    bar.close()

    compiled_rows = compiled[0]
    for index_slice in range(1, row + 1):
        print(index_slice)
        image_row = compiled[index_slice]
        compiled_rows = np.vstack((compiled_rows, image_row))


    cv2.imwrite(f"{path}_sliced.png", compiled_rows)


if __name__ == "__main__":
    main()
