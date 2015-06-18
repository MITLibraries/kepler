# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
from mock import patch, Mock
from requests import HTTPError

from kepler.geoserver import (service_url, put_url, delete_url, put, delete)


pytestmark = pytest.mark.usefixtures('app')
root = 'http://example.com/geoserver/'


@pytest.yield_fixture
def requests():
    patcher = patch('kepler.geoserver.requests')
    yield patcher.start()
    patcher.stop()


class TestGeoServer(object):
    def testServiceUrlGeneratesUrl(self):
        assert service_url(root, 'foo') == '%srest/workspaces/foo/' % root

    def testPutUrlReturnsShapefileUrl(self):
        assert put_url(root, 'foo', 'application/zip') == \
            '%srest/workspaces/mit/datastores/data/file.shp' % root

    def testPutUrlReturnsCoverageUrl(self):
        assert put_url(root, 'foo', 'image/tiff') == \
            '%srest/workspaces/mit/coveragestores/foo/file.geotiff' % root

    def testDeleteUrlReturnsShapefileUrl(self):
        assert delete_url(root, 'foo', 'application/zip') == \
            '%srest/workspaces/mit/datastores/data/featuretypes/foo?recurse=true' % root

    def testDeleteUrlReturnsCoverageUrl(self):
        assert delete_url(root, 'foo', 'image/tiff') == \
            '%srest/workspaces/mit/coveragestores/foo?recurse=true' % root

    def testPutUploadsData(self, requests):
        put(root, 'foo', 'tests/data/bermuda.zip', 'application/zip')
        call = requests.put.call_args
        assert call[1].get('data').name == 'tests/data/bermuda.zip'

    def testPutRaisesHttpErrorWhenUnsuccessful(self, requests):
        requests.put.return_value = Mock(**{'raise_for_status.side_effect': HTTPError})
        with pytest.raises(HTTPError):
            put(root, 'foo', 'tests/data/grayscale.tif', 'image/tiff')

    def testDeleteDeletesResource(self, requests):
        delete(root, 'foo', 'image/tiff')
        url = delete_url(root, 'foo', 'image/tiff')
        requests.delete.assert_called_once_with(url)

    def testDeleteRaisesHttpErrorWhenUnsuccessful(self, requests):
        requests.delete.return_value = Mock(**{'raise_for_status.side_effect': HTTPError})
        with pytest.raises(HTTPError):
            delete(root, 'foo', 'application/zip')
