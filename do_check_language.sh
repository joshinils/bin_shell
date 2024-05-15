#!/usr/bin/env bash

cd check_language_staging || exit

find . -type f \( -name '*.mkv' -o -name '*.mp4' -o -name '*.png' \) -exec mv {} . \;
find . -type d -empty -delete

sort_again_better_new.sh
rm file.html filme_names.csv filme_names.firefox filme_names.txt .movie_languages_meta.pkl > /dev/null 2>&1

find . -maxdepth 1 -type d -exec sh -c 'cd $1; mkdir DVD BD -p; mv -- *DVD*.mkv *DVD*.mp4 *DVD*.png DVD > /dev/null 2>&1; mv -- *BD*.mkv *BD*.mp4 *BD*.png BD > /dev/null 2>&1' shell {} \;
flattendirectory > /dev/null 2>&1
find . -type d -empty -delete
find . -maxdepth 1 -type d -exec sh -c 'cd $1; media_metadata.py *.mkv *.mp4' shell {} \;
flattendirectory > /dev/null 2>&1
find . -type d -empty -delete

mkdir -p ../check_language
mv -n -- * ../check_language
for d in */ ; do
    echo "$d"
    mv -n "$d"/* ../check_language/"$d"
done
find . -type d -empty -delete
cd ..
rmdir --ignore-fail-on-non-empty check_language_staging
