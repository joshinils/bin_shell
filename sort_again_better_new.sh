#!/usr/bin/env bash

mkdir bonus better again new hd-tv-dvd -p > /dev/null 2>&1
mv bonus---*.mkv bonus > /dev/null 2>&1
mv bonus---*.png bonus > /dev/null 2>&1
mv bonus---*.mp4 bonus > /dev/null 2>&1
mv better---*.mkv better > /dev/null 2>&1
mv better---*.png better > /dev/null 2>&1
mv better---*.mp4 better > /dev/null 2>&1
mv again---*.mkv again > /dev/null 2>&1
mv again---*.mp4 again > /dev/null 2>&1
mv again---*.png again > /dev/null 2>&1
mv new---*.mkv new > /dev/null 2>&1
mv new---*.mp4 new > /dev/null 2>&1
mv new---*.png new > /dev/null 2>&1
mv hd-tv-dvd---*.mkv hd-tv-dvd > /dev/null 2>&1
mv hd-tv-dvd---*.mp4 hd-tv-dvd > /dev/null 2>&1
mv hd-tv-dvd---*.png hd-tv-dvd > /dev/null 2>&1

find . -maxdepth 1 \( -iname '*.mkv' -o -iname '*.mp4' \) | sort > filme_names.txt

process_filme_names.py

$HOME/settings/moviepilot/compare_csv_lst.py filme_names.csv /media/wd4-r1/data/filme/filme_names.csv -b -s > file.html
