# -*- coding: utf-8 -*-
from __future__ import absolute_import
import tempfile
import os

from kepler.bag import *
from kepler.bag import _extract_data


def test_extract_returns_pathname(bag):
    assert _extract_data(bag, '.zip') == "%sdata/shapefile.zip" % bag


def test_returns_fgdc_path(bag):
    assert get_fgdc(bag) == "%sdata/fgdc.xml" % bag


def test_returns_shapefile_path(bag):
    assert get_shapefile(bag) == "%sdata/shapefile.zip" % bag


def test_unpacks_bag(bag_upload):
    tmp = tempfile.mkdtemp()
    unpack(bag_upload, tmp)
    assert os.path.isdir(os.path.join(tmp, "bermuda"))
