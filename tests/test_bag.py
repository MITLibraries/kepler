# -*- coding: utf-8 -*-
import unittest
import io

from kepler.bag import *


class FgdcReaderTestCase(unittest.TestCase):
    def testReturnsFgdcByteStream(self):
        with io.open('tests/data/bermuda.zip', 'rb') as fp:
            fgdc = read_fgdc(fp)
        self.assertEqual(fgdc.readlines()[1], b'<metadata xml:lang="en">\n')
