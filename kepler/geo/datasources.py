# -*- coding: utf-8 -*-
from __future__ import absolute_import
from . import (gdal, GDAL_RGB, GDAL_PALETTED,)


class Raster(object):
    def __init__(self, file):
        self.ds = gdal.Open(file)

    def bands(self):
        bands = self.ds.RasterCount
        for i in range(1, bands+1):
            yield self.ds.GetRasterBand(i)

    @property
    def rgb(self):
        return (self.ds.RasterCount == 3 and
            all(band.GetColorInterpretation() in GDAL_RGB for band in self.bands()))

    @property
    def paletted(self):
        return (self.ds.RasterCount == 1 and
            self.ds.GetRasterBand(1).GetColorInterpretation() == GDAL_PALETTED)

    @property
    def width(self):
        return self.ds.RasterXSize

    @property
    def height(self):
        return self.ds.RasterYSize

    def close(self):
        self.ds = None
