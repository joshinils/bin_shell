#!/usr/bin/env python3

import re
import subprocess
from typing import List


def add_ellipses(ls: List[str]) -> List[str]:
    this_index = -1
    prev_number = None
    prev_f = None
    prev_was_match = False
    omitted_count = 0
    ls_return = []

    for f in ls:
        this_index += 1
        matches = re.findall("[0-9]+", f)
        concat_matches = ''.join(matches)

        if len(concat_matches) > 0:
            number_match = int(concat_matches)
        else:
            number_match = -1

        if (        len(concat_matches) > 0 # there are numbers
                and prev_number == number_match -1 # continuous
                and this_index+1 != len(ls) # not last
            ):
            # don't print f
            prev_was_match = True
            omitted_count += 1
            #ls_return.append(f)
        else:
            if prev_was_match:
                if omitted_count > 1:
                    ls_return.append("...")
                    pass
                if this_index+1 != len(ls): # not last
                    ls_return.append(prev_f)
            prev_was_match = False
            ls_return.append(f)
            omitted_count = 0


        # prepare for next iteration
        prev_number = number_match
        prev_f = f
    return ls_return

if __name__ == '__main__':
    ls = add_ellipses( subprocess.run(["ls","-1A"],text=True,stdout=subprocess.PIPE).stdout.splitlines() )
    for i in ls:
        print(i)
