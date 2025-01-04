#!/usr/bin/env bash

flatpak run org.bunkus.mkvtoolnix-gui mkvmerge "$@"
# example call: /app/bin/mkvmerge --ui-language en_US --priority lower --output '/media/l-nas36/data/filme_neu/ingesting/check_language/BD_new_2—  de_en_both/new---Good Morning, Vietnam_1987 - BD RHB (1).mkv' --audio-tracks 1,3,4 --language 0:en --display-dimensions 0:1920x1080 --language 1:en --track-name '1:Surround 5.1' --language 3:de --track-name 3:Stereo --language 4:fr --track-name '4:Surround 5.1' --language 5:en --language 6:de --language 7:de --language 8:fr --language 9:fr '(' '/media/l-nas36/data/filme_neu/ingesting/check_language/BD_new_2—  de_en_both/new---Good Morning, Vietnam_1987 - BD RHB.mkv' ')' --title 'Good Morning Vietnam' --track-order 0:0,0:1,0:3,0:4,0:5,0:6,0:7,0:8,0:9
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

input="${output/\ \(1\)//}"

if [[ -f "$input" ]]; then
    if [[ -f "$output" ]]; then
        echo "Output path: #$output#"
        echo " Input path: #$input#"
        echo touch -r new---Good\ Morning,\ Vietnam_1987\ -\ BD\ RHB.mkv new---Good\ Morning,\ Vietnam_1987\ -\ BD\ RHB\ \(1\).mkv
    fi
fi

