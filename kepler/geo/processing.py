# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import closing
from future.moves.subprocess import check_output
from kepler.geo.datasources import Raster


def compress(file_in, file_out):
    args = ['-co', 'TILED=YES', '-co', 'COMPRESS=JPEG', '-co',
            'BLOCKXSIZE=2048', '-co', 'BLOCKYSIZE=2048',]
    with closing(Raster(file_in)) as ds:
        if ds.paletted:
            args = args + ['-expand', 'rgb', '-co', 'PHOTOMETRIC=YCBCR']
        elif ds.rgb:
            args = args + ['-co', 'PHOTOMETRIC=YCBCR']

    command = ['gdal_translate'] + args + [file_in, file_out]
    check_output(command)
