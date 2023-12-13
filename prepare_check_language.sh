#!/usr/bin/env bash

mkdir check_language -p
mv -- *.mkv check_language
cd check_language || exit

sort_neu_besser_nochmal.sh
firefox -new-window file.html
