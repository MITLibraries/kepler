# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest

from kepler import compose


class KeplerTestCase(unittest.TestCase):
    def testComposeReturnsComposedFunction(self):
        add = lambda x, y: x + y
        inc = lambda x: x + 1
        dbl = lambda x: x * 2
        f = compose(dbl, inc, add)
        self.assertEqual(f(1, 2), 8)
