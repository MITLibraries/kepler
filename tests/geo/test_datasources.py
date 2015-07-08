# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import closing

from kepler.geo.datasources import Raster


class TestRaster(object):
    def testRgbReturnsTrueForRgb(self, rgb_tif):
        with closing(Raster(rgb_tif)) as ds:
            assert ds.rgb

    def testPalettedReturnsTrueForPaletted(self, paletted_tif):
        with closing(Raster(paletted_tif)) as ds:
            assert ds.paletted

    def testWidthReturnsWidth(self, grayscale_tif):
        with closing(Raster(grayscale_tif)) as ds:
            assert ds.width == 600

    def testHeightReturnsHeight(self, grayscale_tif):
        with closing(Raster(grayscale_tif)) as ds:
            assert ds.height == 300
