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

echo "DEBUG: frames=$frames"

# Determine zero padding
padding_length=${#frames}

quality=""
# Choose extension: png for <1000 frames, jpg for more
if [ "$frames" -le 1000 ]; then
    out_ext="png"
else
    out_ext="jpg"
    quality="-q:v 4"
    if [ "$frames" -le 10000 ]; then
        quality="-q:v 2"
    fi
fi

# Build output pattern
out_pattern="$out_dir/${name_no_ext}_frame_%0${padding_length}d.$out_ext"

echo "DEBUG: out_pattern=$out_pattern"

# Check if interval is time-based (ends with s,ms,us,ns,m,h)
if [[ "$interval" =~ ^([0-9]+(\.[0-9]+)?)(s|ms|us|ns|m|h)$ ]]; then
    # Time-based extraction (including fractional seconds)
    num=${BASH_REMATCH[1]}
    unit=${BASH_REMATCH[3]}
    case "$unit" in
        s)   seconds=$num ;;
        ms)  seconds=$(awk "BEGIN{print $num/1000}") ;;
        us)  seconds=$(awk "BEGIN{print $num/1000000}") ;;
        ns)  seconds=$(awk "BEGIN{print $num/1000000000}") ;;
        m)   seconds=$(awk "BEGIN{print $num*60}") ;;
        h)   seconds=$(awk "BEGIN{print $num*3600}") ;;
    esac
    fps=$(awk "BEGIN{print 1/$seconds}")
    ffmpeg -hide_banner -loglevel error -stats -i "$video_file" -vf "fps=$fps" $quality "$out_pattern"
elif [[ "$interval" =~ ^[0-9]+$ ]]; then
    # Frame-based extraction (only for integer intervals)
    ffmpeg -hide_banner -loglevel error -stats -i "$video_file" -vf "select=not(mod(n\,$interval))" -vsync vfr $quality "$out_pattern"
else
    echo "ERROR: Invalid interval format: $interval"
    exit 2
fi

