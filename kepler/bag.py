# -*- coding: utf-8 -*-
from __future__ import absolute_import
from zipfile import ZipFile
import os


def get_fgdc(bag):
    return _extract_data(bag, 'fgdc.xml')


def get_shapefile(bag):
    return _extract_data(bag, '.zip')


def get_geotiff(bag):
    return _extract_data(bag, '.tif')


def unpack(bag, path):
    archive = ZipFile(bag, 'r')
    try:
        archive.extractall(path)
    finally:
        archive.close()
    bagdir = os.listdir(path).pop()
    return os.path.join(path, bagdir)


def _extract_data(bag, endswith):
    data_dir = os.path.join(bag, 'data/')
    for fname in os.listdir(data_dir):
        if fname.endswith(endswith):
            return os.path.join(data_dir, fname)
