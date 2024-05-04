#!/usr/bin/env bash

cd check_language_staging || exit

find . -type f -name '*.mkv' -exec mv {} . \;
find . -type f -name '*.mp4' -exec mv {} . \;
find . -type f -name '*.png' -exec mv {} . \;
find . -type d -empty -delete

sort_again_better_new.sh
rm file.html filme_names.csv filme_names.firefox filme_names.txt .movie_languages_meta.pkl

find . -maxdepth 1 -type d -exec sh -c 'cd $1; mkdir DVD BD -p; mv -- *DVD*.mkv DVD; mv -- *BD*.mkv BD' shell {} \;
find . -maxdepth 1 -type d -exec sh -c 'cd $1; mkdir DVD BD -p; mv -- *DVD*.mp4 DVD; mv -- *BD*.mp4 BD' shell {} \;
find . -maxdepth 1 -type d -exec sh -c 'cd $1; mkdir DVD BD -p; mv -- *DVD*.png DVD; mv -- *BD*.png BD' shell {} \;
flattendirectory
find . -type d -empty -delete
find . -maxdepth 1 -type d -exec sh -c 'cd $1; media_metadata.py *.mkv' shell {} \;
find . -maxdepth 1 -type d -exec sh -c 'cd $1; media_metadata.py *.mp4' shell {} \;
flattendirectory
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
