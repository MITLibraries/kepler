# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
from mock import patch, Mock
from requests import HTTPError

from kepler.geoserver import (service_url, put_url, delete_url, put, delete)


pytestmark = pytest.mark.usefixtures('app')


@pytest.yield_fixture
def requests():
    patcher = patch('kepler.geoserver.requests')
    yield patcher.start()
    patcher.stop()


class TestGeoServer(object):
    def testServiceUrlGeneratesUrl(self):
        assert service_url('http://example.com/geoserver/', 'foo') == \
            'http://example.com/geoserver/rest/workspaces/foo/'

    def testPutUrlReturnsShapefileUrl(self):
        assert put_url('foo', 'application/zip') == \
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/file.shp'

    def testPutUrlReturnsCoverageUrl(self):
        assert put_url('foo', 'image/tiff') == \
            'http://example.com/geoserver/rest/workspaces/mit/coveragestores/foo/file.geotiff'

    def testDeleteUrlReturnsShapefileUrl(self):
        assert delete_url('foo', 'application/zip') == \
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/featuretypes/foo?recurse=true'

    def testDeleteUrlReturnsCoverageUrl(self):
        assert delete_url('foo', 'image/tiff') == \
            'http://example.com/geoserver/rest/workspaces/mit/coveragestores/foo?recurse=true'

    def testPutUploadsData(self, requests):
        put('foo', 'tests/data/bermuda.zip', 'application/zip')
        call = requests.put.call_args
        assert call[1].get('data').name == 'tests/data/bermuda.zip'

    def testPutRaisesHttpErrorWhenUnsuccessful(self, requests):
        requests.put.return_value = Mock(**{'raise_for_status.side_effect': HTTPError})
        with pytest.raises(HTTPError):
            put('foo', 'tests/data/grayscale.tif', 'image/tiff')

    def testDeleteDeletesResource(self, requests):
        delete('foo', 'image/tiff')
        url = delete_url('foo', 'image/tiff')
        requests.delete.assert_called_once_with(url)

    def testDeleteRaisesHttpErrorWhenUnsuccessful(self, requests):
        requests.delete.return_value = Mock(**{'raise_for_status.side_effect': HTTPError})
        with pytest.raises(HTTPError):
            delete('foo', 'application/zip')
