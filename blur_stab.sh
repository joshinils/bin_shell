#!/usr/bin/env bash

#!/usr/bin/env bash

framerate=$(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "${1}")
smoothing_val=$(echo $framerate / 4 | bc)
smoothing=$(( $smoothing_val > 20 ? $smoothing_val : 20 ))

crf=15
out_name="${1}"_stab

# # generate stab data
# mkdir -p trf && \
# ffmpeg -hide_banner -loglevel error -stats -i "${1}" -vf vidstabdetect=accuracy=15:result="trf/${out_name}.trf" -f null - -y &

# blur video
~/Documents/DashcamCleaner_joshinils/dashcamcleaner/cli.py --batch_size 2 --inference_size 1080 -q 10 -w 1080p_medium_mosaic.pt --threshold 0.2 --blur_size 27 -fe 10 -i "${1}" -o "${1}_blurred.mkv" \
&& mkdir -p original && mv "${1}" original \
&& mkdir -p blurred  && mv "${1}_blurred.mkv" blurred &

wait

# apply stab data
ffmpeg -hide_banner -loglevel error -stats -i "blurred/${1}_blurred.mkv" -vf vidstabtransform=zoom=0:crop=black:optzoom=0:smoothing="${smoothing}":input="trf/${out_name}.trf" -crf ${crf} "${out_name}.mkv" -y \
&& mkdir -p stab && mv "${out_name}.mkv" stab \
