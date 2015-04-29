# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import closing

from kepler.geo.datasources import Raster


class TestRaster(object):
    def testRgbReturnsTrueForRgb(self):
        with closing(Raster('tests/data/rgb.tif')) as ds:
            assert ds.rgb

    def testPalettedReturnsTrueForPaletted(self):
        with closing(Raster('tests/data/paletted.tif')) as ds:
            assert ds.paletted

    def testWidthReturnsWidth(self):
        with closing(Raster('tests/data/grayscale.tif')) as ds:
            assert ds.width == 600

    def testHeightReturnsHeight(self):
        with closing(Raster('tests/data/grayscale.tif')) as ds:
            assert ds.height == 300
