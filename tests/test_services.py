# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from mock import patch
from cStringIO import StringIO
from kepler.services.geoserver import GeoServerServiceManager

class GeoServerTestCase(unittest.TestCase):
    def setUp(self):
        self.file = StringIO('Test file')

    def tearDown(self):
        self.file.close()

    def testServiceManagerUploadsShapefile(self):
        with patch('requests.put') as mock:
            mgr = GeoServerServiceManager(url='http://example.com/')
            mgr.upload(self.file)
            self.assertTrue(mock.called)
