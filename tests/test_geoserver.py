# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
import requests
import requests_mock

from kepler.geoserver import GeoService


@pytest.fixture
def adapter(geoserver_resp):
    a = requests_mock.Adapter()
    a.register_uri(requests_mock.ANY, requests_mock.ANY)
    a.register_uri('GET', requests_mock.ANY, json=geoserver_resp)
    return a


@pytest.fixture
def session(adapter):
    s = requests.Session()
    s.mount('mock://', adapter)
    return s


def test_put_uploads_data(session, adapter, bag_upload):
    m = adapter.register_uri('PUT', requests_mock.ANY)
    geoserver = GeoService(session, 'mock://example.com/', 'mit', 'data')
    geoserver.put('foo', bag_upload, 'application/zip')
    req = m.request_history.pop()
    assert req.text.name == bag_upload


def test_put_returns_shapefile_id(session, bag_upload):
    geoserver = GeoService(session, 'mock://example.com/', 'mit', 'data')
    layer = geoserver.put('foo', bag_upload, 'application/zip')
    assert layer == 'mit:shapefile1'


def test_put_returns_geotiff_id(session, bag_tif_upload):
    geoserver = GeoService(session, 'mock://example.com', 'mit', 'data')
    layer = geoserver.put('foo', bag_tif_upload, 'image/tiff')
    assert layer == 'mit:geotiff1'
