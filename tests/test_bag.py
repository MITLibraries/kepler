# -*- coding: utf-8 -*-
from __future__ import absolute_import
import tempfile
import os

import pytest
from mock import patch

from kepler.bag import *
from kepler.bag import _extract_data
from kepler.exceptions import FileNotFound, InvalidAccessLevel


def test_extract_returns_pathname(bag):
    assert _extract_data(bag, '.zip') == "%sdata/shapefile.zip" % bag


def test_extract_raises_exception(bag):
    with pytest.raises(FileNotFound):
        _extract_data(bag, '.wut')


def test_returns_fgdc_path(bag):
    assert get_fgdc(bag) == "%sdata/fgdc.xml" % bag


def test_returns_shapefile_path(bag):
    assert get_shapefile(bag) == "%sdata/shapefile.zip" % bag


def test_returns_shapefile_name(bag):
    assert get_shapefile_name(bag) == 'SDE_DATA_BD_A8GNS_2003'


def test_unpacks_bag(bag_upload):
    tmp = tempfile.mkdtemp()
    unpack(bag_upload, tmp)
    assert os.path.isfile(os.path.join(tmp, 'bag-info.txt'))


def test_get_datatype_returns_shapefile(bag):
    assert get_datatype(bag) == 'shapefile'


def test_get_datatype_returns_geotiff(bag_tif):
    assert get_datatype(bag_tif) == 'geotiff'


def test_get_access_returns_access(bag):
    assert get_access(bag) == 'Public'


def test_get_access_raises_exception(bag):
    with patch('kepler.bag.rights_mapper') as rights:
        rights.return_value = 'Super Secret'
        with pytest.raises(InvalidAccessLevel):
            get_access(bag)
