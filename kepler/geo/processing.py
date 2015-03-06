# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
from contextlib import closing
import math
from future.moves.subprocess import check_output
from kepler.geo.datasources import Raster


def compress(file_in, file_out):
    """Compress and tile a GeoTIFF.

    This will call out to ``gdal_translate`` using JPEG compression and
    a block size of 2048x2048. If the input file is a single band paletted
    image this will expand to RGB. Finally, any RGB images will be converted
    to YCbCr color space.

    .. note:: Both parameters are file names, not file handles.

    :param file_in: input file name
    :param file_out: output file name
    """

    args = ['-co', 'TILED=YES', '-co', 'COMPRESS=JPEG', '-co',
            'BLOCKXSIZE=2048', '-co', 'BLOCKYSIZE=2048',]
    with closing(Raster(file_in)) as ds:
        if ds.paletted:
            args = args + ['-expand', 'rgb', '-co', 'PHOTOMETRIC=YCBCR']
        elif ds.rgb:
            args = args + ['-co', 'PHOTOMETRIC=YCBCR']
    command = ['gdal_translate'] + args + [file_in, file_out]
    check_output(command)


def pyramid(file_in):
    """Add overviews to a GeoTIFF.

    Calls out to ``gdaladdo`` to add overview images to the input file. This
    will operate directly on the input file.

    .. note:: The parameter is a file name, not a file handle.

    :param file_in: input file name
    """

    with closing(Raster(file_in)) as ds:
        levels = compute_levels(ds.width, ds.height)
    if levels:
        command = ['gdaladdo', '-r', 'average', file_in] + levels
        check_output(command)


def compute_levels(w, h):
    """Compute optimal list of overview levels.

    Given the supplied width and height of an image, and assuming a block size
    of 2048x2048, calculate the best levels for generating overviews. If
    ``max(w, h)`` is less than 2048 an empty list is returned.

    :param w: width of image
    :param h: height of image
    :returns: list of levels
    """

    num_levels = int(math.ceil(math.log((max(w, h)/2048), 2)))
    return [2**y for y in range(1, num_levels + 1)]
