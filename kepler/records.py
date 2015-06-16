# -*- coding: utf-8 -*-
from __future__ import absolute_import
import uuid
import six
from slugify import slugify
from ogre.record import Record
from ogre.xml import parse
from ogre.fields import String, Enum


def create_record(metadata, parser, **kwargs):
    record = parse(metadata, parser)
    record.update(kwargs)
    return MitRecord(**record)


def rights_mapper(term):
    """Maps access rights from FGDC to canonical GeoBlacklight value."""
    if term.lower().startswith('unrestricted'):
        return 'Public'
    elif term.lower().startswith('restricted'):
        return 'Restricted'
    return term


def geometry_mapper(term):
    """Maps layer geometry from FGDC to canonical GeoBlacklight value."""
    if 'point' in term.lower():
        return 'Point'
    elif 'string' in term.lower():
        return 'Line'
    elif any(v_type in term.lower() for v_type in ['polygon', 'chain']):
        return 'Polygon'
    return term


def make_uuid_value(value):
    """Convert a value into the proper type for creating a UUID.

    In python 2 ``uuid.uuid5`` takes a byte string while in python 3 it
    takes a unicode string. This function will convert the provided value
    to the correct type based on which version of python is being used.

    :param value: the byte string or unicode string to convert
    """

    if isinstance(value, six.binary_type):
        if six.PY3:
            value = value.decode('utf-8')
    elif isinstance(value, six.text_type):
        if six.PY2:
            value = value.encode('utf-8')
    return value


class MitRecord(Record):
    dc_rights_s = Enum(enums=['Public', 'Restricted'], mapper=rights_mapper)
    layer_geom_type_s = Enum(enums=['Point', 'Line', 'Polygon', 'Raster',
                             'Scanned Map', 'Paper Map', 'Mixed'],
                             mapper=geometry_mapper)
    _filename = String()

    @property
    def layer_slug_s(self):
        if not self._filename:
            return None
        return slugify(self._filename, to_lower=True)
