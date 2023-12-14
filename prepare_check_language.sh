#!/usr/bin/env bash

mkdir check_language -p
mv -- *.mkv check_language
cd check_language || exit

sort_again_better_new.sh
firefox -new-window file.html
