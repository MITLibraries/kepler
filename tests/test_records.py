# -*- coding: utf-8 -*-
from __future__ import absolute_import
import uuid

from slugify import slugify
from ogre.xml import FGDCParser

from kepler.records import MitRecord, create_record


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
        r = MitRecord(_filename='BD_A8GNS_2003')
        assert r.layer_slug_s == slugify('BD_A8GNS_2003', to_lower=True)
