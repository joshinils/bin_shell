#!/usr/bin/env bash

mkdir bonus -p > /dev/null 2>&1
mv *bonus*.mkv bonus > /dev/null 2>&1

rmdir bonus > /dev/null 2>&1

mkdir better again new hd-tv-dvd -p > /dev/null 2>&1
mv better---*.mkv better > /dev/null 2>&1
mv again---*.mkv again > /dev/null 2>&1
mv new---*.mkv new > /dev/null 2>&1
mv hd-tv-dvd---*.mkv hd-tv-dvd > /dev/null 2>&1

find . -maxdepth 1 \( -iname '*.mkv' -o -iname '*.mp4' \) | sort > filme_names.txt

process_filme_names.py

$HOME/settings/moviepilot/compare_csv_lst.py filme_names.csv /media/wd4-r1/data/filme/filme_names.csv -b -s > file.html
