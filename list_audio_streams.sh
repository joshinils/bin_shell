#!/usr/bin/env bash

echo "" > temp_sortable
find * -maxdepth 0 -type f \( -iname "*.mp4" -o -iname "*.mkv" -o -iname "*.mov" -o -iname "*.webm" \) -print0 | sort --zero-terminated | while IFS= read -r -d '' file; do
    # echo "file = $file"
    printf "%2s $file\n" "$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "${file}" | wc -w)" >> temp_sortable
done

cat temp_sortable | sort -h
rm temp_sortable

