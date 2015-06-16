# -*- coding: utf-8 -*-
from __future__ import absolute_import
import uuid
import base64

from ogre.record import Record
from ogre.xml import parse
from ogre.fields import Enum


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


class MitRecord(Record):
    dc_rights_s = Enum(enums=['Public', 'Restricted'], mapper=rights_mapper)
    layer_geom_type_s = Enum(enums=['Point', 'Line', 'Polygon', 'Raster',
                             'Scanned Map', 'Paper Map', 'Mixed'],
                             mapper=geometry_mapper)

    @property
    def layer_slug_s(self):
        uid = uuid.UUID(self.uuid)
        b64 = base64.urlsafe_b64encode(uid.bytes[:8])
        return "mit-%s" % b64.decode('ascii').rstrip('=')
