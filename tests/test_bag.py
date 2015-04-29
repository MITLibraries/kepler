# -*- coding: utf-8 -*-
from __future__ import absolute_import

from kepler.bag import *


class TestFgdcReader(object):
    def testReturnsFgdcByteStream(self, bag):
        fgdc = read_fgdc(bag)
        assert fgdc.readlines()[1] == b'<metadata xml:lang="en">\n'
