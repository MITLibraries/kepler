# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from mock import patch
from kepler.geo.processing import (compress, compute_levels, pyramid)


class ProcessingTestCase(unittest.TestCase):
    @patch('kepler.geo.processing.check_output')
    def testCompressRunsCommandWithArgs(self, sub_mock):
        compress('tests/data/paletted.tif', 'out.tif')
        sub_mock.assert_called_once_with(
            ['gdal_translate',
                '-co', 'TILED=YES',
                '-co', 'COMPRESS=JPEG',
                '-co', 'BLOCKXSIZE=2048',
                '-co', 'BLOCKYSIZE=2048',
                '-expand', 'rgb',
                '-co', 'PHOTOMETRIC=YCBCR',
                'tests/data/paletted.tif', 'out.tif'])

    @patch('kepler.geo.processing.compute_levels', return_value=[2, 4, 8])
    @patch('kepler.geo.processing.check_output')
    def testPyramidRunsCommandWithArgs(self, sub_mock, comp_mock):
        pyramid('tests/data/rgb.tif')
        sub_mock.assert_called_once_with(
            ['gdaladdo', '-r', 'average', 'tests/data/rgb.tif', 2, 4, 8])

    @patch('kepler.geo.processing.compute_levels', return_value=[])
    @patch('kepler.geo.processing.check_output')
    def testPyramidSkipsOverviewsWhenNotNeeded(self, sub_mock, comp_mock):
        pyramid('tests/data/rgb.tif')
        self.assertEqual(sub_mock.call_count, 0)

    def testComputeLevelsReturnsListOfOverviewLevels(self):
        self.assertEqual(compute_levels(2049, 2048), [2])
        self.assertEqual(compute_levels(16000, 20000), [2, 4, 8, 16])

    def testComputeLevelsReturnsEmptyListForNoLevels(self):
        self.assertEqual(compute_levels(2048, 2048), [])
