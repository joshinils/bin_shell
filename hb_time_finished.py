#!/usr/bin/env python3

import datetime
import subprocess


# https://stackoverflow.com/a/136368
def tail(path, lines=20):
    with open(path, "rb") as f:
        total_lines_wanted = lines

        BLOCK_SIZE = 1024
        f.seek(0, 2)
        block_end_byte = f.tell()
        lines_to_go = total_lines_wanted
        block_number = -1
        blocks = []
        while lines_to_go > 0 and block_end_byte > 0:
            if (block_end_byte - BLOCK_SIZE > 0):
                f.seek(block_number * BLOCK_SIZE, 2)
                blocks.append(f.read(BLOCK_SIZE))
            else:
                f.seek(0, 0)
                blocks.append(f.read(block_end_byte))
            lines_found = blocks[-1].count(b'\n')
            lines_to_go -= lines_found
            block_end_byte -= BLOCK_SIZE
            block_number -= 1
        all_read_text = b''.join(reversed(blocks))
        return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:]).decode().split("\n")


subprocess.run(["screen", "-S", "handbrake", "-p", "0", "-X", "hardcopy"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


last_lines = tail("/tmp/handbrake/hardcopy.0", 60)

delta_finished = None
for line in last_lines:
    parts = line.split(", ETA ")
    if len(parts) < 2:
        continue

    h, rest = parts[1].split("h", 1)

    if not h.isdigit():
        continue
    else:
        h = int(h)

    m, rest = rest.split("m", 1)
    if not m.isdigit():
        continue
    else:
        m = int(m)

    s, rest = rest.split("s", 1)
    if not s.isdigit():
        continue
    else:
        s = int(s)

    delta_finished = datetime.timedelta(hours=h, minutes=m, seconds=s)

if delta_finished is None:
    exit()

time_done: datetime.datetime = datetime.datetime.now() + delta_finished
days_left = delta_finished.days

if days_left > 0:
    print(f"{days_left}d", time_done.strftime("%a %H:%M:%S"))
else:
    print(time_done.strftime("%H:%M:%S"))