# -*- coding: utf-8 -*-
from __future__ import absolute_import

from kepler import compose


class TestKepler(object):
    def testComposeReturnsComposedFunction(self):
        add = lambda x, y: x + y
        inc = lambda x: x + 1
        dbl = lambda x: x * 2
        f = compose(dbl, inc, add)
        assert f(1, 2) == 8
