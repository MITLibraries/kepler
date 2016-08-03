# -*- coding: utf-8 -*-
from __future__ import absolute_import

import arrow
from mock import patch
from ogre.xml import FGDCParser

from kepler.records import *


class TestRecordCreation(object):
    def testCreateRecordReturnsMetadataRecord(self, fgdc):
        record = create_record(fgdc, FGDCParser)
        assert record.dc_title_s == 'Bermuda (Geographic Feature Names, 2003)'
        assert record.dc_rights_s == 'Public'

    def testCreateRecordUsesUserSuppliedValues(self, fgdc):
        record = create_record(fgdc, FGDCParser, dc_rights_s='Restricted',
                               dct_provenance_s='MIT')
        assert record.dc_rights_s == 'Restricted'
        assert record.dct_provenance_s == 'MIT'


class TestMitRecord(object):
    def testAccessConstraintMapped(self):
        r = MitRecord(dc_rights_s='Unrestricted Access Online')
        assert r.dc_rights_s == 'Public'

    def testGeometryTypeMapped(self):
        r = MitRecord(layer_geom_type_s='Entity point')
        assert r.layer_geom_type_s == 'Point'

    def testSlugGenerated(self):
        r = MitRecord(dc_identifier_s='c8921f5a-eac7-509b-bac5-bd1b2cb202dc')
        assert r.layer_slug_s == 'mit-yJIfWurHUJs'

    def testDefaultsToMIT(self):
        r = MitRecord()
        assert r.dct_provenance_s == 'MIT'

    def test_sets_geoblacklight_version(self):
        r = MitRecord()
        assert r.geoblacklight_version == '1.0'

    def test_defaults_to_now_for_modified_time(self):
        now = arrow.utcnow()
        r = MitRecord()
        assert r.layer_modified_dt is not None
        assert now.replace(minutes=-1) < arrow.get(r.layer_modified_dt) < \
               now.replace(minutes=+1)


def testRightsMapperNormalizesTerm():
    assert rights_mapper('Unrestricted layer') == 'Public'
    assert rights_mapper('rEsTrIcted layer') == 'Restricted'
    assert rights_mapper('Public') == 'Public'


def testGeometryMapperNormalizesTerm():
    assert geometry_mapper('a point or two') == 'Point'
    assert geometry_mapper('here is a string, yo') == 'Line'
    assert geometry_mapper('however, this is a polygon') == 'Polygon'
    assert geometry_mapper('Line') == 'Line'
