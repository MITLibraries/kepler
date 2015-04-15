# -*- coding: utf-8 -*-
from __future__ import absolute_import
from mock import patch, Mock

from requests import HTTPError

from tests import BaseTestCase
from kepler.geoserver import (service_url, put_url, delete_url, put, delete)


class GeoServerTestCase(BaseTestCase):
    def testServiceUrlGeneratesUrl(self):
        self.assertEqual(service_url('http://example.com/geoserver/', 'foo'),
                         'http://example.com/geoserver/rest/workspaces/foo/')

    def testPutUrlReturnsShapefileUrl(self):
        self.assertEqual(put_url('foo', 'application/zip'),
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/file.shp')

    def testPutUrlReturnsCoverageUrl(self):
        self.assertEqual(put_url('foo', 'image/tiff'),
            'http://example.com/geoserver/rest/workspaces/mit/coveragestores/foo/file.geotiff')

    def testDeleteUrlReturnsShapefileUrl(self):
        self.assertEqual(delete_url('foo', 'application/zip'),
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/featuretypes/foo?recurse=true')

    def testDeleteUrlReturnsCoverageUrl(self):
        self.assertEqual(delete_url('foo', 'image/tiff'),
            'http://example.com/geoserver/rest/workspaces/mit/coveragestores/foo?recurse=true')

    @patch('requests.put')
    def testPutUploadsData(self, mock):
        put('foo', 'bar', 'application/zip')
        url = put_url('foo', 'application/zip')
        mock.assert_called_once_with(url, data='bar',
                                     headers={'Content-type': 'application/zip'})

    @patch('requests.put')
    def testPutRaisesHttpErrorWhenUnsuccessful(self, mock):
        mock.return_value = Mock(**{'raise_for_status.side_effect': HTTPError})
        with self.assertRaises(HTTPError):
            put('foo', 'bar', 'image/tiff')

    @patch('requests.delete')
    def testDeleteDeletesResource(self, mock):
        delete('foo', 'image/tiff')
        url = delete_url('foo', 'image/tiff')
        mock.assert_called_once_with(url)

    @patch('requests.delete')
    def testDeleteRaisesHttpErrorWhenUnsuccessful(self, mock):
        mock.return_value = Mock(**{'raise_for_status.side_effect': HTTPError})
        with self.assertRaises(HTTPError):
            delete('foo', 'application/zip')
