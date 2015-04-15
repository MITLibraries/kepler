# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app
from kepler.services.solr import SolrServiceManager
from mock import patch
from tests import BaseTestCase


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