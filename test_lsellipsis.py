#!/usr/bin/env python3

import unittest
from lsellipsis import add_ellipses

class Test_add_ellipses(unittest.TestCase):

    def test_0(self):
        input = [""]
        output = [""]

        self.assertEqual(add_ellipses(input), output)

    def test_1(self):
        input = ["a11b",
                 "a12b",
                 "a13b"]
        output = ["a11b",
                 "...",
                 "a13b"]
        self.assertEqual(add_ellipses(input), output)

    def test_2(self):
        input = ["a00b",
                 "a11b",
                 "a12b",
                 "a13b",
                 "a15b"]
        output = ["a00b",
                  "a11b",
                  "...",
                  "a13b",
                  "a15b"]
        self.assertEqual(add_ellipses(input), output)

    def test_10(self):
        input = ["a00b",
                 "a11b",
                 "a12b",
                 "a13b",
                 "a15b",
                 "a16b",
                 "a17b",
                 "a20b",
                 "a21b",
                 "a222",
                 "a22b",
                 "a23b",
                 "a25b",
                 "a26b",
                 "a27b",
                 "a2-7b",
                 "a2.7b",
                 "a28b",
                 "a29b",
                 "a2b",
                 "a2c7b",
                 "b30b",
                 "c31c",
                 "c31d",
                 "d32e",
                 ".foo",
                 "single"]
        output = ["a00b",
                  "a11b",
                  "...",
                  "a13b",
                  "a15b",
                  "...",
                  "a17b",
                  "a20b",
                  "a21b",
                  "a222",
                  "a22b",
                  "a23b",
                  "a25b",
                  "...",
                  "a27b",
                  "a2-7b",
                  "a2.7b",
                  "a28b",
                  "a29b",
                  "a2b",
                  "a2c7b",
                  "b30b",
                  "c31c",
                  "c31d",
                  "d32e",
                  ".foo",
                  "single"]
        self.assertEqual(add_ellipses(input), output)


if __name__ == '__main__':
    unittest.main()
