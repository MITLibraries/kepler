# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from mock import patch, Mock
import requests
from tests import StringIO
from kepler.services.geoserver import GeoServerServiceManager

class GeoServerTestCase(unittest.TestCase):
    def setUp(self):
        self.file = StringIO(u'Test file')
        self.mgr = GeoServerServiceManager('http://example.com/')

    def tearDown(self):
        self.file.close()

    @patch('requests.put')
    def testServiceManagerUploadsShapefile(self, mock):
        self.mgr.upload(self.file)
        self.assertTrue(mock.called)

    @patch('requests.put')
    def testUploadRaisesErrorOnNon200Response(self, mock):
        attrs = {'raise_for_status.side_effect': requests.exceptions.HTTPError}
        mock.return_value = Mock(**attrs)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.mgr.upload(self.file)
