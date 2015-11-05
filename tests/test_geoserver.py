# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
from mock import patch, Mock
from requests import HTTPError

from kepler.geoserver import *
from kepler.geoserver import _get_json


pytestmark = pytest.mark.usefixtures('app')
root = 'http://example.com/geoserver/'


@pytest.yield_fixture
def requests():
    patcher = patch('kepler.geoserver.requests')
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def http_error():
    return Mock(**{'raise_for_status.side_effect': HTTPError})


@pytest.fixture
def ftypes():
    m = Mock()
    m.json.return_value = {'dataStore': {'featureTypes': 'foobar'}}
    return m


@pytest.fixture
def cstore():
    m = Mock()
    m.json.return_value = {'coverageStore': {'coverages': 'foobar'}}
    return m


@pytest.fixture
def ftype():
    m = Mock()
    m.json.return_value = {'featureTypes': {'featureType': [{'name': 'foo'}]}}
    return m


@pytest.fixture
def cvg():
    m = Mock()
    m.json.return_value = {'coverages': {'coverage': [{'name': 'foo'}]}}
    return m


class TestGeoServer(object):
    def testWmsUrlReturnsUrlForAccessLevel(self):
        assert wms_url('Public') == 'http://example.com/geoserver/wms'
        assert wms_url('Restricted') == 'http://example.com/secure-geoserver/wms'

    def testWfsUrlReturnsUrlForAccessLevel(self):
        assert wfs_url('Public') == 'http://example.com/geoserver/wfs'
        assert wfs_url('Restricted') == 'http://example.com/secure-geoserver/wfs'

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

    def testGetJsonUsesAuth(self, requests):
        _get_json(root)
        call = requests.get.call_args
        assert call[1].get('auth') == ('username', 'password')

    def testPutUploadsData(self, requests, bag_upload):
        put(root, 'foo', bag_upload, 'application/zip')
        call = requests.put.call_args
        assert call[1].get('data').name == bag_upload

    def testPutUsesBasicAuth(self, requests, bag_upload):
        put(root, 'foo', bag_upload, 'application/zip')
        call = requests.put.call_args
        assert call[1].get('auth') == ('username', 'password')

    def testPutReturnsLayerId(self, requests, bag_upload):
        with patch('kepler.geoserver.layer_id') as mock:
            mock.return_value = 'foo:bar'
            assert put(root, 'foo', bag_upload, 'application/zip') == 'foo:bar'

    def testPutCallsLayerIdWithCorrectUrl(self, requests, bag_upload):
        with patch('kepler.geoserver.layer_id') as mock:
            put(root, 'http://example.com/foo/file.shp', bag_upload,
                'application/zip')
        assert mock.call_args[0][0] == '%srest/workspaces/mit/datastores/data' % root

    def testPutRaisesHttpErrorWhenUnsuccessful(self, requests, grayscale_tif,
                                               http_error):
        requests.put.return_value = http_error
        with pytest.raises(HTTPError):
            put(root, 'foo', grayscale_tif, 'image/tiff')

    def testDeleteDeletesResource(self, requests):
        delete(root, 'foo', 'image/tiff')
        url = delete_url(root, 'foo', 'image/tiff')
        requests.delete.assert_called_once_with(url)

    def testDeleteRaisesHttpErrorWhenUnsuccessful(self, requests, http_error):
        requests.delete.return_value = http_error
        with pytest.raises(HTTPError):
            delete(root, 'foo', 'application/zip')

    def testFeatureTypesRequestsJSON(self, requests, ftypes):
        requests.get.return_value = ftypes
        feature_types('http://example.com')
        kwargs = requests.get.call_args[1]
        assert kwargs.get('headers') == {'Accept': 'application/json'}

    def testFeatureTypesReturnsFeatureTypesURL(self, requests, ftypes):
        requests.get.return_value = ftypes
        assert feature_types('http://example.com/') == 'foobar'

    def testFeatureTypesRaisesHttpError(self, requests, http_error):
        requests.get.return_value = http_error
        with pytest.raises(HTTPError):
            feature_types('http://example.com/')

    def testFeatureTypeNameRequestsJSON(self, requests, ftype):
        requests.get.return_value = ftype
        feature_type_name('http://example.com')
        kwargs = requests.get.call_args[1]
        assert kwargs.get('headers') == {'Accept': 'application/json'}

    def testFeatureTypeNameReturnsLayerName(self, requests, ftype):
        requests.get.return_value = ftype
        assert feature_type_name('http://example.com') == 'foo'

    def testFeatureTypeNameRaisesHttpError(self, requests, http_error):
        requests.get.return_value = http_error
        with pytest.raises(HTTPError):
            feature_type_name('http://example.com')

    def testCoveragesRequestsJSON(self, requests, cstore):
        requests.get.return_value = cstore
        coverages('http://example.com')
        kwargs = requests.get.call_args[1]
        assert kwargs.get('headers') == {'Accept': 'application/json'}

    def testCoveragesReturnsCoveragesURL(self, requests, cstore):
        requests.get.return_value = cstore
        assert coverages('http://example.com') == 'foobar'

    def testCoveragesRaisesHttpError(self, requests, http_error):
        requests.get.return_value = http_error
        with pytest.raises(HTTPError):
            coverages('http://example.com')

    def testCoverageNameRequestsJSON(self, requests, cvg):
        requests.get.return_value = cvg
        coverage_name('http://example.com')
        kwargs = requests.get.call_args[1]
        assert kwargs.get('headers') == {'Accept': 'application/json'}

    def testCoverageNameReturnsLayerName(self, requests, cvg):
        requests.get.return_value = cvg
        assert coverage_name('http://example.com') == 'foo'

    def testCoverageNameRaisesHttpError(self, requests, http_error):
        requests.get.return_value = http_error
        with pytest.raises(HTTPError):
            coverage_name('http://example.com')

    def testLayerIdReturnsIdForShapefile(self, requests, ftypes, ftype):
        requests.get.side_effect = [ftypes, ftype]
        assert layer_id('http://example.com', 'application/zip') == 'mit:foo'

    def testLayerIdReturnsIdForGeoTiff(self, requests, cstore, cvg):
        requests.get.side_effect = [cstore, cvg]
        assert layer_id('http://example.com', 'image/tiff') == 'mit:foo'
