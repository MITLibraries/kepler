# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
import requests
import requests_mock

from kepler.geoserver import GeoService


@pytest.fixture
def session(adapter):
    s = requests.Session()
    s.mount('mock://', adapter)
    return s


def test_put_uploads_data(session, bag_upload):
    geoserver = GeoService(session, 'mock://example.com/geoserver', 'mit', 'data')
    geoserver.put(bag_upload, 'shapefile', 'test')
    a = session.get_adapter('mock://example.com')
    assert a.call_count == 4
