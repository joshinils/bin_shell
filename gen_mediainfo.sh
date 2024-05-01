#!/usr/bin/env bash

find . -maxdepth 1 -type f \( -name "*.mkv" -o -name "*.mp4" \) -exec sh -c 'mediainfo -f "$1" > "$1.mediainfo"' shell {} \;
code . -n  -- *.mediainfo
