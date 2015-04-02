# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
import io
import uuid
from slugify import slugify
from kepler.records import MitRecord, create_record
from ogre.xml import FGDCParser


class RecordCreationTestCase(unittest.TestCase):
    def setUp(self):
        self.metadata = io.open('tests/data/shapefile/fgdc.xml',
                                encoding='utf-8')

    def tearDown(self):
        self.metadata.close()

    def testCreateRecordReturnsMetadataRecord(self):
        record = create_record(self.metadata, FGDCParser)
        self.assertEqual(record.dc_title_s,
                         'Bermuda (Geographic Feature Names, 2003)')
        self.assertEqual(record.dc_rights_s, 'Public')

    def testCreateRecordUsesUserSuppliedValues(self):
        record = create_record(self.metadata, FGDCParser,
                               dc_rights_s='Restricted', dct_provenance_s='MIT')
        self.assertEqual(record.dc_rights_s, 'Restricted')
        self.assertEqual(record.dct_provenance_s, 'MIT')


class MitRecordTestCase(unittest.TestCase):
    def testAccessConstraintMapped(self):
        r = MitRecord(dc_rights_s='Unrestricted Access Online')
        self.assertEqual(r.dc_rights_s, 'Public')

    def testGeometryTypeMapped(self):
        r = MitRecord(layer_geom_type_s='Entity point')
        self.assertEqual(r.layer_geom_type_s, 'Point')

    def testUuidGeneratedFromByteString(self):
        uuid_ns = uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu')
        r = MitRecord(_filename=b'BD_A8GNS_2003', _namespace=b'arrowsmith.mit.edu')
        self.assertEqual(r.uuid, str(uuid.uuid5(uuid_ns, 'BD_A8GNS_2003')))

    def testUuidGeneratedFromUnicodeString(self):
        uuid_ns = uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu')
        r = MitRecord(_filename=u'BD_A8GNS_2003', _namespace=u'arrowsmith.mit.edu')
        self.assertEqual(r.uuid, str(uuid.uuid5(uuid_ns, 'BD_A8GNS_2003')))

    def testIdentifierEqualsUuid(self):
        r = MitRecord(_filename='BD_A8GNS_2003', _namespace='arrowsmith.mit.edu')
        self.assertEqual(r.uuid, r.dc_identifier_s)

    def testSlugGenerated(self):
        r = MitRecord(_filename='BD_A8GNS_2003')
        self.assertEqual(r.layer_slug_s, slugify('BD_A8GNS_2003', to_lower=True))
