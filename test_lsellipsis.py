#!/usr/bin/env python3

import unittest

from lsellipsis import add_ellipses


class test_0add_ellipses(unittest.TestCase):

    def test_00(self):
        input = [""]
        output = [""]

        self.assertEqual(add_ellipses(input), output)

    def test_01(self):
        input = [
            "a11b",
            "a12b",
            "a13b"
        ]
        output = [
            "a11b",
            "...",
            "a13b"
        ]
        self.assertEqual(add_ellipses(input), output)

    def test_02a(self):
        input = [
            "a00b",
            "a11b",
            "a12b",
            "a13b",
            "a15b"
        ]
        output = [
            "a00b",
            "a11b",
            "...",
            "a13b",
            "a15b"
        ]
        self.assertEqual(add_ellipses(input), output)

    def test_02b(self):
        input = [
            "a00b",
            "a11b",
            "a12b",
            "a13b",
            "a15b",
            "a25b"
        ]
        output = [
            "a00b",
            "a11b",
            "...",
            "a13b",
            "a15b",
            "a25b"
        ]
        self.assertEqual(add_ellipses(input), output)

    def test_03(self):
        input = [
            "a",
            "a1",
            "a2",
            "a4",
            "b"
        ]
        output = input
        self.assertEqual(add_ellipses(input), output)

    def test_04(self):
        input = [
            "a",
            "a1",
            "a2",
            "a3",
            "a4",
            "b"
        ]
        output = [
            "a",
            "a1",
            "...",
            "a4",
            "b"
        ]
        self.assertEqual(add_ellipses(input), output)

    def test_05(self):
        input = [
            "a",
            "a1",
            "a2",
            "a3",
            "a5",
            "b"
        ]
        output = [
            "a",
            "a1",
            "...",
            "a3",
            "a5",
            "b"
        ]
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
