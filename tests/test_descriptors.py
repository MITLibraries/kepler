# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from kepler.descriptors import *

class DescriptorsTestCase(unittest.TestCase):
    def testEnumDefaultsToNoopMapper(self):
        class Record(object):
            cat = Enum(name='cat', enums=['Lucy Cat', 'Hot Pocket'])

        r = Record()
        r.cat = 'Lucy Cat'
        self.assertEqual(r.cat, 'Lucy Cat')

    def testEnumAppliesProvidedMapper(self):
        class Record(object):
            cat = Enum(name='cat', enums=['LUCY CAT', 'HOT POCKET'],
                       mapper=lambda x: x.upper())

        r = Record()
        r.cat = 'Hot Pocket'
        self.assertEqual(r.cat, 'HOT POCKET')
