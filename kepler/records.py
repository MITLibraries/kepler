# -*- coding: utf-8 -*-
from __future__ import absolute_import
import base64
import json
import uuid

import arrow
from ogre.record import Record
from ogre.xml import parse


def create_record(metadata, parser, **kwargs):
    record = parse(metadata, parser)
    record.update(kwargs)
    return MitRecord(solr_geom=(record['_bbox_w'], record['_bbox_e'],
                                record['_bbox_n'], record['_bbox_s']),
                     **record)


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
    dct_provenance_s = 'MIT'
    geoblacklight_version = '1.0'

    @Record.dc_rights_s.setter
    def dc_rights_s(self, value):
        super(MitRecord, MitRecord).dc_rights_s.fset(self, rights_mapper(value))

    @Record.layer_geom_type_s.setter
    def layer_geom_type_s(self, value):
        super(MitRecord, MitRecord).\
            layer_geom_type_s.fset(self, geometry_mapper(value))

    @property
    def layer_slug_s(self):
        uid = uuid.UUID(self.dc_identifier_s)
        b64 = base64.urlsafe_b64encode(uid.bytes[:8])
        return "mit-%s" % b64.decode('ascii').rstrip('=')

    @property
    def layer_modified_dt(self):
        return self.__dict__.setdefault('_layer_modified_dt',
                 arrow.utcnow().format('YYYY-MM-DDTHH:mm:ss') + 'Z')

    @layer_modified_dt.setter
    def layer_modified_dt(self, value):
        self._layer_modified_dt = arrow.get(value).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
