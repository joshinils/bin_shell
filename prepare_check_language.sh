#!/usr/bin/env bash

check_language="check_language_staging"
mkdir $check_language -p
mv -- *.mkv *.mp4 *.png $check_language
cd $check_language || exit

sort_again_better_new.sh

if (( $# > 0 )); then
    firefox -new-window file.html
fi
