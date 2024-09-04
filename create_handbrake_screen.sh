#!/usr/bin/env bash

# to be invoked by cron

# check if a screen session with name "handbrake" exists,
# if not, create it

echo $RANDOM > /dev/null
if ! screen -list | grep -q "handbrake"; then
    # sleep random amount between 0.1 and 0.9 seconds
    sleep "$(echo "$(shuf -i 1000-9000 -n 1)/10000" | bc -l)"
else
    exit 1
fi

if ! screen -list | grep -q "handbrake"; then
    if [ "$(find -- /media/wd4-r1/data/filme_neu/untouched/*.json 2>/dev/null | wc -l)" != 0 ] ; then
        screen -dm -S handbrake /usr/bin/zsh -c "/media/wd4-r1/data/filme_neu/untouched/do.sh -i '${1}'"
    else
        screen -dm -S handbrake /usr/bin/zsh -c "/media/wd4-r1/data_36/filme_neu/untouched/do.sh -i '${1}'"
    fi
fi
