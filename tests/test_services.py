# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from mock import patch, Mock
import requests
import pysolr
from io import BytesIO
from kepler.services.geoserver import GeoServerServiceManager
from kepler.services.solr import SolrServiceManager

class GeoServerTestCase(unittest.TestCase):
    def setUp(self):
        self.file = BytesIO(u'Test file'.encode('utf-8'))
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

class SolrTestCase(unittest.TestCase):
    def setUp(self):
        self.testRecord = {
            'uuid': 'test_uuid'
        }
        self.testBadRecord = {
            'uid': 'test_uuid' # key not 'uuid'
        }
        self.testUrl = 'http://localhost:8983/solr/geoblacklight/'
        self.mgr = SolrServiceManager(self.testUrl)

    def tearDown(self):
        pass

    @patch('pysolr.Solr.add')
    def testSolrServiceManagerPost(self, mock):
        response = self.mgr.postMetaDataToServer([self.testRecord])
        mock.assert_called_once_with([self.testRecord])
        print mock.return_value

    def testValidateRecord(self):
        self.mgr._validateRecord(self.testRecord)

        with self.assertRaises(AttributeError) as attributeError:
            self.mgr._validateRecord(self.testBadRecord)
