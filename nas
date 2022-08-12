#!/bin/bash
ssh -t nials@nals-NAS "cd \"$PWD\"; exec \$SHELL --login"

