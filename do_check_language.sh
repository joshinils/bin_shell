#!/usr/bin/env bash

cd check_language || exit

find . -type f -name '*.mkv' -exec mv {} . \;
find . -type d -empty -delete

sort_again_better_new.sh
rm file.html filme_names.csv filme_names.firefox filme_names.txt .movie_languages_meta.pkl

find . -maxdepth 1 -type d -exec sh -c 'cd $1; mkdir DVD BD -p; mv -- *DVD*.mkv DVD; mv -- *BD*.mkv BD' shell {} \;
flattendirectory
find . -type d -empty -delete
find . -maxdepth 1 -type d -exec sh -c 'cd $1; media_metadata.py *.mkv' shell {} \;
flattendirectory
find . -type d -empty -delete
