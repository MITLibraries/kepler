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
        self.mgr = GeoServerServiceManager('http://example.com/geoserver',
                                           'mit', 'data')

    def tearDown(self):
        self.file.close()

    @patch('requests.put')
    def testServiceManagerUploadsShapefile(self, mock):
        self.mgr.upload(self.file, 'application/zip')
        mock.assert_called_with(self.mgr.base_url + 'file.shp', data=self.file,
                                headers={'Content-type': 'application/zip'})

    @patch('requests.put')
    def testUploadRaisesErrorOnNon200Response(self, mock):
        attrs = {'raise_for_status.side_effect': requests.exceptions.HTTPError}
        mock.return_value = Mock(**attrs)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.mgr.upload(self.file, 'application/zip')

    def testServiceManagerConstructsUrl(self):
        self.assertEqual(self.mgr.base_url,
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/')

    @patch('requests.delete')
    def testDeleteRemovesLayer(self, mock):
        self.mgr.delete('GOODBYE_WORLD')
        mock.assert_called_once_with(
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/featuretypes/GOODBYE_WORLD?recurse=true')

    @patch('requests.delete')
    def testDeleteRaisesErrorOnNon200Response(self, mock):
        attrs = {'raise_for_status.side_effect': requests.exceptions.HTTPError}
        mock.return_value = Mock(**attrs)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.mgr.delete('GOODBYE_WORLD')


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

    def testValidateRecord(self):
        self.mgr._validateRecord(self.testRecord)

        with self.assertRaises(AttributeError) as attributeError:
            self.mgr._validateRecord(self.testBadRecord)