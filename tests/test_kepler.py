# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from mock import Mock

from kepler import compose, make_tempfile


class TestKepler(object):
    def testComposeReturnsComposedFunction(self):
        add = lambda x, y: x + y
        inc = lambda x: x + 1
        dbl = lambda x: x * 2
        f = compose(dbl, inc, add)
        assert f(1, 2) == 8


def testMakeTempfileReturnsNoneForNoData():
    assert make_tempfile() is None


def testMakeTempfileCreatesTempfile():
    fname = make_tempfile(Mock(filename='foobar.zip'))
    assert os.path.exists(fname)
    os.remove(fname)


def testMakeTempfileAppendsFilename():
    fname = make_tempfile(Mock(filename='foobar.zip'))
    try:
        assert fname.endswith('-foobar.zip')
    finally:
        os.remove(fname)
