#!/usr/bin/env bash

flatpak run org.bunkus.mkvtoolnix-gui mkvmerge "$@"
output=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output)
            output="$2"
            break
            ;;
        *)
            shift
            ;;
    esac
done

input="${output/\ \(1\)/}"

if [ -f "$input" ]; then
    if [ -f "$output" ]; then
        touch -r "$input" "$output"
    fi
fi

