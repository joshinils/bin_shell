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
# shellcheck disable=SC2317  # Don't warn about unreachable commands in this function
error() {
    local lineno=$1
    local linecode
    linecode=$(sed -n "${lineno}p" "$SCRIPT_PATH")
    echo "$SCRIPT_PATH:$lineno ERROR: '$linecode'"
}
trap 'error "${LINENO}"' ERR



function main() {
    if [ -z "$1" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        echo "Usage: $0 <video_file> [interval]"
        echo "    interval: every nth frame (default=1), or time unit (e.g. 1s, 100ms, 2m, 1h)"
        exit 1
    fi

    video_file="$1"
    interval="${2:-1}"

    validate_interval "$interval"

    base_name="$(basename -- "$video_file")"
    name_no_ext="${base_name%.*}"
    out_dir="${name_no_ext}.d/extracted_thumbs"
    mkdir -p "$out_dir"

    frames=$(get_frame_count "$video_file")
    IFS='|' read -r out_ext quality <<< "$(choose_output_format "$frames")"

    check_free_space "$out_dir"

    extract_frames "$video_file" "$interval" "$out_dir" "$name_no_ext" "$out_ext" "$quality"

    rename_frames "$out_dir" "$name_no_ext" "$out_ext"
}

function validate_interval() {
    local interval="$1"
    # Validate interval: must be strictly greater than 0
    if [[ "$interval" =~ ^-?[0-9]+(\.[0-9]+)?(s|ms|us|ns|m|h)?$ ]]; then
        local num
        num=$(echo "$interval" | grep -oE '^-?[0-9]+(\.[0-9]+)?')
        if (( $(echo "$num <= 0" | bc -l) )); then
            echo "ERROR: Interval must be greater than zero."
            exit 2
        fi
    else
        echo "ERROR: Invalid interval format: $interval"
        exit 3
    fi
}

function get_frame_count() {
    local video_file="$1"

    local frames
    frames=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 -- "$video_file")
    frames=${frames//,/}
    if ! [[ "$frames" =~ ^[0-9]+$ ]]; then
        frames=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 -- "$video_file")
    fi
    echo "$frames"
}

function choose_output_format() {
    # png for <1000 frames, jpg for more
    local frames="$1"

    local out_ext quality
    if [[ "$frames" =~ ^[0-9]+$ ]] && [ "$frames" -le 1000 ]; then
        out_ext="png"
        quality=""
    else
        out_ext="jpg"
        quality="-q:v 4"
        if [ "$frames" -le 10000 ]; then
            quality="-q:v 2"
        fi
    fi
    echo "$out_ext|$quality"
}

function check_free_space() {
    local out_dir="$1"

    local min_free_gb=100
    local out_fs free_gb
    out_fs=$(df -P "$out_dir" | tail -1 | awk '{print $4}')  # df returns blocks, usually 1K per block
    free_gb=$((out_fs / 1024 / 1024))
    if [ "$free_gb" -lt "$min_free_gb" ]; then
        echo "WARNING: Not enough free space on the output filesystem. At least ${min_free_gb}G required, but only ${free_gb}G available."
        if [ -t 1 ] || is_screen_attached; then
            IFS= read -r -t 10 -p "Do you want to continue anyway? (y/N): " answer
            case "$answer" in
                [Yy]* ) ;;
                * ) exit 10 ;;
            esac
        else
            exit 10
        fi
    fi
}

function extract_frames() {
    local video_file="$1"
    local interval="$2"
    local out_dir="$3"
    local name_no_ext="$4"
    local out_ext="$5"
    local quality="$6"

    # Use ffmpeg to extract frames with filenames based on the timestamp (PTS in ms)
    if [[ "$interval" =~ ^([0-9]+(\.[0-9]+)?)(s|ms|us|ns|m|h)$ ]]; then  # Time-based extraction
        local num unit seconds fps
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
        ffmpeg_tqdm -hide_banner -loglevel error -stats -vsync 0 -i "$video_file" -copyts -fps_mode passthrough -enc_time_base 0.001 -vf "fps=$fps" ${quality:+$quality} -f image2 -frame_pts 1 "$out_dir/${name_no_ext}_frame_%d.$out_ext"
    elif [[ "$interval" =~ ^[0-9]+$ ]]; then  # Frame-based extraction (only for integer intervals)
        ffmpeg_tqdm -hide_banner -loglevel error -stats -vsync 0 -i "$video_file" -copyts -fps_mode passthrough -enc_time_base 0.001 -vf "select=not(mod(n\,$interval))" -f image2 -frame_pts 1 "$out_dir/${name_no_ext}_frame_%d.$out_ext"
    else
        echo "ERROR: Invalid interval format: $interval"
        exit 2
    fi
}

function rename_frames() {
    # Rename files to human-readable timestamps
    local out_dir="$1"
    local name_no_ext="$2"
    local out_ext="$3"

    local files_list total_files count
    files_list=("$out_dir/${name_no_ext}_frame_"*".${out_ext}")
    total_files=${#files_list[@]}
    count=0
    for f in "${files_list[@]}"; do
        pts=$(echo "$f" | sed -E 's/.*_frame_([0-9]+)\..*/\1/')
        ts=$(awk -v ms="$pts" 'BEGIN { s=int(ms/1000); ms=ms%1000; h=int(s/3600); m=int((s%3600)/60); s=s%60; printf("%02d-%02d-%02d.%03d", h, m, s, ms) }')
        mv -n "$f" "$out_dir/${name_no_ext}_$ts.$out_ext"
        count=$((count+1))
        echo "$count" | pv -n -s "$total_files" > /dev/null
    done | pv -n -s "$total_files" > /dev/null
}

function is_screen_attached() {
    # Check if running in screen or tmux and if attached

    if [ -n "$STY" ]; then
        # In screen, check if attached
        if screen -ls | grep -q "Attached"; then
            return 0
        else
            return 1
        fi
    elif [ -n "$TMUX" ]; then
        # In tmux, check if attached
        if tmux list-clients 2>/dev/null | grep -q "(attached)"; then
            return 0
        else
            return 1
        fi
    fi
    return 1
}

[[ ${BASH_SOURCE[0]} = "$0" ]] && main "$@"; exit
