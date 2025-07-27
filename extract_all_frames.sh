#!/usr/bin/env bash

video_file="$1"
interval="${2:-1}"

if [ -z "$video_file" ] || [ "$video_file" == "-h" ] || [ "$video_file" == "--help" ]; then
    echo "Usage: $0 <video_file> [interval]"
    echo "    interval: every nth frame (default=1), or time unit (e.g. 1s, 100ms, 2m, 1h)"
    exit 1
fi

base_name="$(basename -- "$video_file")"
name_no_ext="${base_name%.*}"
out_dir="${name_no_ext}.${interval}.d"
mkdir -p "$out_dir"

# Get total frame count
frames=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$video_file")
frames=${frames//,/}
if ! [[ "$frames" =~ ^[0-9]+$ ]]; then
    frames=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 "$video_file")
fi
frames=${frames:-10000}

# Determine zero padding
padding_length=${#frames}

# Choose extension: png for <1000 frames, jpg for more
if [ "$frames" -le 1000 ]; then
    out_ext="png"
    quality=""
else
    out_ext="jpg"
    quality="-q:v 4"
    if [ "$frames" -le 10000 ]; then
        quality="-q:v 2"
    fi
fi

# Build output pattern
out_pattern="$out_dir/${name_no_ext}_frame_%0${padding_length}d.$out_ext"

# Check if interval is time-based (ends with s,ms,us,ns,m,h)
if [[ "$interval" =~ ^[0-9]+(s|ms|us|ns|m|h)$ ]]; then
    # Time-based extraction
    ffmpeg -hide_banner -loglevel error -stats -i "$video_file" -vf "fps=1/$interval" "$quality" "$out_pattern"
else
    # Frame-based extraction
    ffmpeg -hide_banner -loglevel error -stats -i "$video_file" -vf "select=not(mod(n\,$interval))" -vsync vfr "$quality" "$out_pattern"
fi

