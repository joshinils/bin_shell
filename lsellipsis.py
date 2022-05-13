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
    prev_char_match = None

    for f in ls:
        this_index += 1
        digit_matches = re.findall(r"[0-9]+", f)
        concat_matches = ''.join(digit_matches)

        char_matches = re.findall(r"^.+?(?=[0-9])", f)
        concat_char_match = ''.join(char_matches)

        if len(concat_matches) > 0:
            number_match = int(concat_matches)
        else:
            number_match = -1

        if(len(concat_matches) > 0  # there are numbers
            and prev_number == number_match - 1  # continuous
            and prev_char_match == concat_char_match  # beginning string is same
           ):
            # don't print f
            prev_was_match = True  # for next iteration
            omitted_count += 1  # for next iteration

            if this_index + 1 == len(ls):  # is last
                ls_return.append("...")
                ls_return.append(f)
                return ls_return
            prev_f = f  # for next iteration
        else:
            if prev_was_match:
                prev_was_match = False  # for next iteration

                if omitted_count > 1:
                    ls_return.append("...")
                ls_return.append(prev_f)

            ls_return.append(f)
            omitted_count = 0  # reset

        # for next iteration
        prev_number = number_match
        prev_char_match = concat_char_match

    return ls_return


if __name__ == '__main__':
    ls = add_ellipses(subprocess.run(["ls", "-1A"], text=True, stdout=subprocess.PIPE).stdout.splitlines())
    for i in ls:
        print(i)
