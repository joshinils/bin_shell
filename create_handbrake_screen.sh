#!/usr/bin/env bash

# to be invoked by cron

# check if a screen session with name "handbrake" exists,
# if not, create it

if ! screen -list | grep -q "handbrake"; then
    screen -dm -S handbrake /usr/bin/zsh -c "/media/wd4-r1/data/filme_neu/untouched/do.sh -i"
fi
