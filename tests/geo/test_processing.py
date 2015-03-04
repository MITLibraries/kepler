# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from mock import patch
from kepler.geo.processing import compress


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
