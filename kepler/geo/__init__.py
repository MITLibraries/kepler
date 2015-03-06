# -*- coding: utf-8 -*-
from __future__ import absolute_import
try:
    from osgeo import gdal
except ImportError:
    import gdal


GDAL_RGB = (gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand)
GDAL_PALETTED = gdal.GCI_PaletteIndex
