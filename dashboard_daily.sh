#!/usr/bin/env bash

LC_ALL=de_DE.utf8 date +"%A, %d. %B %Y W%W T%j %Z %:::z"
curl -s "wttr.in/Frohnau?format=%F0%9F%8C%84%D+A+%F0%9F%8C%85%S+A+%F0%9F%8F%9E%EF%B8%8F%z+A+%F0%9F%8C%87%s+A+%F0%9F%8C%8C%d+A+%m%M" | sed 's/:[0-9]\{2\} A//g'; echo
curl -s "wttr.in/Frohnau?format=%c%t+%F0%9F%92%A7%p/3h+%F0%9F%92%A8%w+%F0%9F%8C%AB%EF%B8%8F+%h+%P+%F0%9F%94%86%u/12"; echo
