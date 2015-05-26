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

    def testUuidGeneratedFromByteString(self):
        uuid_ns = uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu')
        r = MitRecord(_filename=b'BD_A8GNS_2003', _namespace=b'arrowsmith.mit.edu')
        assert r.uuid == str(uuid.uuid5(uuid_ns, 'BD_A8GNS_2003'))

    def testUuidGeneratedFromUnicodeString(self):
        uuid_ns = uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu')
        r = MitRecord(_filename=u'BD_A8GNS_2003', _namespace=u'arrowsmith.mit.edu')
        assert r.uuid == str(uuid.uuid5(uuid_ns, 'BD_A8GNS_2003'))

    def testIdentifierEqualsUuid(self):
        r = MitRecord(_filename='BD_A8GNS_2003', _namespace='arrowsmith.mit.edu')
        assert r.uuid == r.dc_identifier_s

    def testSlugGenerated(self):
        r = MitRecord(_filename='BD_A8GNS_2003')
        assert r.layer_slug_s == slugify('BD_A8GNS_2003', to_lower=True)
