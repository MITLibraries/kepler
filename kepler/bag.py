# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import re
import shutil
from zipfile import ZipFile

from kepler.exceptions import FileNotFound, InvalidAccessLevel
from kepler.records import rights_mapper


def get_fgdc(bag):
    return _extract_data(bag, '.xml')


def get_shapefile(bag):
    return _extract_data(bag, '.zip')


def get_shapefile_name(bag):
    shp = get_shapefile(bag)
    with ZipFile(shp) as zf:
        files = zf.namelist()
    for f in files:
        if f.endswith('.shp'):
            return os.path.splitext(os.path.basename(f))[0]


def get_geotiff(bag):
    return _extract_data(bag, '.tif')


def unpack(bag, path):
    archive = ZipFile(bag, 'r')
    try:
        archive.extractall(path)
        bagdir = os.path.join(path, os.listdir(path)[0])
        for f in os.listdir(bagdir):
            shutil.move(os.path.join(bagdir, f), path)
        shutil.rmtree(bagdir)
    finally:
        archive.close()
    return path


def get_datatype(bag):
    try:
        get_shapefile(bag)
        return 'shapefile'
    except FileNotFound:
        get_geotiff(bag)
        return 'geotiff'


def get_access(bag):
    with open(get_fgdc(bag)) as fp:
        match = re.search('<accconst>(?P<access>.*)</accconst>', fp.read())
    access = rights_mapper(match.group('access'))
    if access not in ('Public', 'Restricted'):
        raise InvalidAccessLevel(access)
    return access


def _extract_data(bag, endswith):
    data_dir = os.path.join(bag, 'data/')
    for fname in os.listdir(data_dir):
        if fname.endswith(endswith):
            return os.path.join(data_dir, fname)
    raise FileNotFound("No file in bag ending with %s" % endswith)
