# -*- coding: utf-8 -*-
from __future__ import absolute_import

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

    def testReferencesDictIsMergedWithSupplied(self, fgdc):
        refs = {'dct_references_s': {'http://www.w3.org/1999/xhtml': 'foobaz'}}
        with patch('kepler.records.parse') as mock:
            mock.return_value = refs
            record = create_record(fgdc, FGDCParser, uuid='uuid-1',
                                   dct_references_s={'http://schema.org/url': 'foobar'})
        assert record.dct_references_s == {
            'http://www.w3.org/1999/xhtml': 'foobaz',
            'http://schema.org/url': 'foobar',
        }


class TestMitRecord(object):
    def testAccessConstraintMapped(self):
        r = MitRecord(dc_rights_s='Unrestricted Access Online')
        assert r.dc_rights_s == 'Public'

    def testGeometryTypeMapped(self):
        r = MitRecord(layer_geom_type_s='Entity point')
        assert r.layer_geom_type_s == 'Point'

    def testSlugGenerated(self):
        r = MitRecord(uuid='c8921f5a-eac7-509b-bac5-bd1b2cb202dc')
        assert r.layer_slug_s == 'mit-yJIfWurHUJs'


def testRightsMapperNormalizesTerm():
    assert rights_mapper('Unrestricted layer') == 'Public'
    assert rights_mapper('rEsTrIcted layer') == 'Restricted'
    assert rights_mapper('Public') == 'Public'


def testGeometryMapperNormalizesTerm():
    assert geometry_mapper('a point or two') == 'Point'
    assert geometry_mapper('here is a string, yo') == 'Line'
    assert geometry_mapper('however, this is a polygon') == 'Polygon'
    assert geometry_mapper('Line') == 'Line'
