#!/usr/bin/env bash


: '
prompt:
this file shall use ffmpeg to extract all frames of a video (by default).
the first positional argument is the video, the second is every nth frame it shall extract, default=1.
this shall create a folder of the same name as the video appended ".d" in which the frames shall be names the same as the video but appended "frame_000.ext" where the count of leading zeros is defined by the total count of frames in the video.
the extension should be picked by what is fastest to extract and reasonably small filesize for long videos so as not to flood the harddrive.
the resolution shall be exactly the same as in the video.
optionally, the second argument can have a time unit at the end (like ns, s, m, h), then every nth unit of time shall a frame be extracted instead.

look at #file:gen_thumbs for inspiration'


set -e
set -o pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
error() {
    local lineno=$1
    local linecode
    linecode=$(sed -n "${lineno}p" "$SCRIPT_PATH")
    echo "$SCRIPT_PATH:$lineno ERROR: '$linecode'"
}
trap 'error "${LINENO}"' ERR



if [ -z "$1" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: $0 <video_file> [interval]"
    echo "    interval: every nth frame (default=1), or time unit (e.g. 1s, 100ms, 2m, 1h)"
    exit 1
fi


video_file="$1"
interval="${2:-1}"

# Validate interval: must be strictly greater than 0
if [[ "$interval" =~ ^-?[0-9]+(\.[0-9]+)?(s|ms|us|ns|m|h)?$ ]]; then
    # Extract numeric part
    num=$(echo "$interval" | grep -oE '^-?[0-9]+(\.[0-9]+)?')

    if (( $(echo "$num <= 0" | bc -l) )); then
        echo "ERROR: Interval must be greater than zero."
        exit 2
    fi
else
    echo "ERROR: Invalid interval format: $interval"
    exit 3
fi

base_name="$(basename -- "$video_file")"
name_no_ext="${base_name%.*}"
out_dir="${name_no_ext}.${interval}.d/extracted_thumbs"
mkdir -p "$out_dir"

# Get total frame count
frames=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 -- "$video_file")
frames=${frames//,/}
if ! [[ "$frames" =~ ^[0-9]+$ ]]; then
    frames=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 -- "$video_file")
fi

if [[ "$frames" =~ ^[0-9]+$ ]]; then
    padding_length=${#frames}
else
    echo "WARNING: Could not determine frame count, using default padding length of 5."
    frames="unknown"
    padding_length=5
fi

quality=""
# Choose extension: png for <1000 frames, jpg for more
if [[ "$frames" =~ ^[0-9]+$ ]] && [ "$frames" -le 1000 ]; then
    out_ext="png"
else
    out_ext="jpg"
    quality="-q:v 4"
    if [ "$frames" -le 10000 ]; then
        quality="-q:v 2"
    fi
fi

# Use ffmpeg to extract frames with filenames based on the timestamp (PTS in ms)
if [[ "$interval" =~ ^([0-9]+(\.[0-9]+)?)(s|ms|us|ns|m|h)$ ]]; then  # Time-based extraction
    num="${BASH_REMATCH[1]}"
    unit="${BASH_REMATCH[3]}"
    case "$unit" in
        s)   seconds=$num ;;
        ms)  seconds=$(awk "BEGIN{print $num/1000}") ;;
        us)  seconds=$(awk "BEGIN{print $num/1000000}") ;;
        ns)  seconds=$(awk "BEGIN{print $num/1000000000}") ;;
        m)   seconds=$(awk "BEGIN{print $num*60}") ;;
        h)   seconds=$(awk "BEGIN{print $num*3600}") ;;
    esac
    fps=$(awk "BEGIN{print 1/$seconds}")
    ffmpeg -hide_banner -loglevel error -stats -vsync 0 -copyts -fps_mode passthrough -enc_time_base 0.001 -i "$video_file" -vf "fps=$fps" ${quality:+$quality} -f image2 -frame_pts 1 "$out_dir/${name_no_ext}_frame_%d.$out_ext"
elif [[ "$interval" =~ ^[0-9]+$ ]]; then  # Frame-based extraction (only for integer intervals)
    ffmpeg -hide_banner -loglevel error -stats -vsync 0 -copyts -fps_mode passthrough -enc_time_base 0.001 -i "$video_file" -vf "select=not(mod(n\,$interval))" -f image2 -frame_pts 1 "$out_dir/${name_no_ext}_frame_%d.$out_ext"
else
    echo "ERROR: Invalid interval format: $interval"
    exit 2
fi

# Rename files to human-readable timestamps
for f in "$out_dir/${name_no_ext}_frame_"*".${out_ext}"; do
    pts=$(echo "$f" | sed -E 's/.*_frame_([0-9]+)\..*/\1/')
    ts=$(awk -v ms="$pts" 'BEGIN { s=int(ms/1000); ms=ms%1000; h=int(s/3600); m=int((s%3600)/60); s=s%60; printf("%02d-%02d-%02d.%03d", h, m, s, ms) }')
    mv -n "$f" "$out_dir/${name_no_ext}_$ts.$out_ext"
done
