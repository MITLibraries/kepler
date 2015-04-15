# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io

from mock import Mock, patch
from tests import BaseTestCase

from kepler.tasks import *


class TasksTestCase(BaseTestCase):

    @patch('kepler.tasks.put')
    def testUploadToGeoserverUploadsData(self, mock):
        record, data = Mock(_filename='foo'), Mock()
        upload_to_geoserver(record, data, 'application/shp')
        mock.assert_called_once_with('foo', data, 'application/shp')

    @patch('pysolr.Solr.add')
    def testIndexRecordAddsRecordToSolr(self, mock):
        record = Mock()
        record.as_dict = Mock(return_value={'uuid': 'foobar'})
        index_record(record)
        mock.assert_called_once_with([{'uuid': 'foobar'}])

    def testMakeRecordCreatesNewRecord(self):
        bag = io.open('tests/data/bermuda.zip', 'rb')
        record, data = make_record(Mock(name='foobar'), bag)
        self.assertEqual(record.dc_title_s,
                         u'Bermuda (Geographic Feature Names, 2003)')
