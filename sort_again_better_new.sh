#!/usr/bin/env bash

mkdir bonus better again new hd-tv-dvd -p > /dev/null 2>&1

declare -a media_types=(
    "bonus"
    "better"
    "again"
    "new"
    "hd-tv-dvd"
)

for m_type in "${media_types[@]}"; do
    find . -maxdepth 1 -regex "\./\([0-9]\{3\}_\(_TV\|MED\|DVD\|_BD\)_\)*${m_type}---.*\.\(mkv\|mp4\|png\)" -exec mv {} "$m_type" \; > /dev/null 2>&1
done

find . -maxdepth 1 \( -iname '*.mkv' -o -iname '*.mp4' \) | sort > filme_names.txt

process_filme_names.py

$HOME/settings/moviepilot/compare_csv_lst.py filme_names.csv /media/wd4-r1/data/filme/filme_names.csv -b -s > file.html
