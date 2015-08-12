# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import closing

from mock import patch

from kepler.geo import *


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


class TestProcessing(object):
    @patch('kepler.geo.check_output')
    def testCompressRunsCommandWithArgs(self, sub_mock, paletted_tif):
        compress(paletted_tif, 'out.tif')
        sub_mock.assert_called_once_with(
            ['gdal_translate',
                '-co', 'TILED=YES',
                '-co', 'COMPRESS=JPEG',
                '-co', 'BLOCKXSIZE=2048',
                '-co', 'BLOCKYSIZE=2048',
                '-expand', 'rgb',
                '-co', 'PHOTOMETRIC=YCBCR',
                paletted_tif, 'out.tif'])

    @patch('kepler.geo.check_output')
    def testCompressSkipsExpandingRGB(self, sub_mock, rgb_tif):
        compress(rgb_tif, 'out.tif')
        sub_mock.assert_called_once_with(
            ['gdal_translate',
                '-co', 'TILED=YES',
                '-co', 'COMPRESS=JPEG',
                '-co', 'BLOCKXSIZE=2048',
                '-co', 'BLOCKYSIZE=2048',
                '-co', 'PHOTOMETRIC=YCBCR',
                rgb_tif, 'out.tif'])

    @patch('kepler.geo.compute_levels', return_value=[2, 4, 8])
    @patch('kepler.geo.check_output')
    def testPyramidRunsCommandWithArgs(self, sub_mock, comp_mock, rgb_tif):
        pyramid(rgb_tif)
        sub_mock.assert_called_once_with(
            ['gdaladdo', '-r', 'average', rgb_tif, 2, 4, 8])

    @patch('kepler.geo.compute_levels', return_value=[])
    @patch('kepler.geo.check_output')
    def testPyramidSkipsOverviewsWhenNotNeeded(self, sub_mock, comp_mock, rgb_tif):
        pyramid(rgb_tif)
        assert sub_mock.call_count == 0

    def testComputeLevelsReturnsListOfOverviewLevels(self):
        assert compute_levels(2049, 2048) == [2]
        assert compute_levels(16000, 20000) == [2, 4, 8, 16]

    def testComputeLevelsReturnsEmptyListForNoLevels(self):
        assert compute_levels(2048, 2048) == []
