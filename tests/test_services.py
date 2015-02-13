# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app
from io import BytesIO
from kepler.services.geoserver import GeoServerServiceManager
from kepler.services.solr import SolrServiceManager
from mock import patch, Mock
from tests import BaseTestCase
from tests import unittest
import pysolr
import requests

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

class SolrTestCase(BaseTestCase):
    def setUp(self):
        super(SolrTestCase, self).setUp()
        
        self.testRecord = {
            'uuid': 'test_uuid'
        }
        self.testBadRecord = {
            'uid': 'test_uuid' # key not 'uuid'
        }
        self.testUrl = current_app.config['SOLR_URL']
        self.mgr = SolrServiceManager(self.testUrl)

    @patch('pysolr.Solr.add')
    def testSolrServiceManagerPost(self, mock):
        response = self.mgr.postMetaDataToServer([self.testRecord])
        mock.assert_called_once_with([self.testRecord])
        print mock.return_value

    def testValidateRecord(self):
        self.mgr._validateRecord(self.testRecord)

        with self.assertRaises(AttributeError) as attributeError:
            self.mgr._validateRecord(self.testBadRecord)