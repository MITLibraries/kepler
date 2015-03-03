# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app
from io import BytesIO
from kepler.services.geoserver import GeoServerResource
from kepler.services.solr import SolrServiceManager
from mock import patch, Mock
from tests import BaseTestCase
from tests import unittest
import pysolr
from requests import HTTPError


class GeoServerResourceTestCase(unittest.TestCase):
    def setUp(self):
        self.data = BytesIO(u'Test file'.encode('utf-8'))

    @patch('requests.put')
    def testPutUploadsData(self, mock):
        r = GeoServerResource()
        r._put = 'http://example.com'
        r.mimetype = 'application/zip'
        r.put(self.data)
        mock.assert_called_once_with('http://example.com', data=self.data,
                                     headers={'Content-type': 'application/zip'})

    @patch('requests.put')
    def testPutRaisesErrorWhenUnsuccessful(self, mock):
        r = GeoServerResource()
        r._put = 'http://example.com'
        r.mimetype = 'application/zip'
        attrs = {'raise_for_status.side_effect': HTTPError}
        mock.return_value = Mock(**attrs)
        with self.assertRaises(HTTPError):
            r.put(self.data)

    @patch('requests.delete')
    def testDeleteDeletesData(self, mock):
        r = GeoServerResource()
        r._delete = 'http://example.com'
        r.delete()
        mock.assert_called_once_with('http://example.com')

    @patch('requests.delete')
    def testDeleteRaisesErrorWhenUnsuccessful(self, mock):
        r = GeoServerResource()
        r._delete = 'http://example.com'
        attrs = {'raise_for_status.side_effect': HTTPError}
        mock.return_value = Mock(**attrs)
        with self.assertRaises(HTTPError):
            r.delete()


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