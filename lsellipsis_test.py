#!/usr/bin/env python3

import unittest
from lsellipsis import add_ellipses

class Test_add_ellipses(unittest.TestCase):

    def test_1(self):
        input = [""]
        output = [""]
        ls = add_ellipses(input)
        self.assertEqual(ls, output)

if __name__ == '__main__':
    unittest.main()
