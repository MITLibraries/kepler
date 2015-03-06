# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from contextlib import closing
from kepler.geo.datasources import Raster


class RasterTestCase(unittest.TestCase):
    def testRgbReturnsTrueForRgb(self):
        with closing(Raster('tests/data/rgb.tif')) as ds:
            self.assertTrue(ds.rgb)

    def testPalettedReturnsTrueForPaletted(self):
        with closing(Raster('tests/data/paletted.tif')) as ds:
            self.assertTrue(ds.paletted)

    def testWidthReturnsWidth(self):
        with closing(Raster('tests/data/grayscale.tif')) as ds:
            self.assertEqual(ds.width, 600)

    def testHeightReturnsHeight(self):
        with closing(Raster('tests/data/grayscale.tif')) as ds:
            self.assertEqual(ds.height, 300)
