# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
import arrow
import json
from kepler.records import GeoRecord, MitRecord
from kepler.exceptions import InvalidDataError


class GeoRecordTestCase(unittest.TestCase):
    def testRecordInitializesFromData(self):
        r = GeoRecord(dc_rights_s='Public')
        self.assertEqual(r.dc_rights_s, 'Public')

    def testEnumRaisesExceptionForUnknownValue(self):
        with self.assertRaises(InvalidDataError):
            GeoRecord(dc_rights_s='Level 8')

    def testStringFieldStripsWhitespaceByDefault(self):
        r = GeoRecord(dc_title_s='Geothermal resources of New Mexico ')
        self.assertEqual(r.dc_title_s, 'Geothermal resources of New Mexico')

    def testGeoRssConstructsRssString(self):
        r = GeoRecord(_bbox_w='-20.5', _bbox_e='20', _bbox_s='-10',
                      _bbox_n='10.0')
        self.assertEqual(r.georss_box_s, '-10 -20.5 10.0 20')

    def testDateTimeConstructsDateTime(self):
        r = GeoRecord(layer_modified_dt='2015-01-01T12:12:12Z')
        self.assertEqual(r.layer_modified_dt.year, 2015)

    def testDateTimeUsesDefault(self):
        r = GeoRecord()
        self.assertEqual(r.layer_modified_dt.year, arrow.now().year)

    def testSolrBboxConstructsBboxString(self):
        r = GeoRecord(_bbox_w='-20.5', _bbox_e='20', _bbox_s='-10',
                      _bbox_n='10.0')
        self.assertEqual(r.solr_bbox, '-20.5 -10 20 10.0')

    def testSolrGeomConstructsGeomString(self):
        r = GeoRecord(_bbox_w='-20.5', _bbox_e='20', _bbox_s='-10',
                      _bbox_n='10.0')
        self.assertEqual(r.solr_geom, 'ENVELOPE(-20.5, 20, 10.0, -10)')

    def testIntegerFieldConvertsToInteger(self):
        r = GeoRecord(solr_year_i='1999')
        self.assertEqual(r.solr_year_i, 1999)

    def testSetFieldRemovesDuplicates(self):
        r = GeoRecord(dc_creator_sm=['Bubbles', 'Bubbles'])
        self.assertEqual(r.dc_creator_sm, set(['Bubbles']))

    def testGeoRssPointConstructsRssString(self):
        r = GeoRecord(_lat='45', _lon='-180')
        self.assertEqual(r.georss_point_s, '45 -180')

    def testAsDictReturnsReferencesAsJson(self):
        references = {
            'http://schema.org/Person': 'Britney Spears',
        }
        r = GeoRecord(dct_references_s=references)
        self.assertEqual(r.as_dict().get('dct_references_s'),
                         json.dumps(references))

    def testGeoRecordCanBeRepresentedAsDictionary(self):
        time = arrow.now()
        r = GeoRecord(uuid='0-8-3', dc_title_s='Today, in the world of cats',
                      _lat='-23', _lon='97', layer_modified_dt=time)
        self.assertEqual(dict((k, v) for k,v in r.as_dict().items() if v),
            {'uuid': '0-8-3', 'dc_title_s': 'Today, in the world of cats',
             'georss_point_s': '-23 97', 'layer_modified_dt': time})


class MitRecordTestCase(unittest.TestCase):
    def testAccessConstraintMapped(self):
        r = MitRecord(dc_rights_s='Unrestricted Access Online')
        self.assertEqual(r.dc_rights_s, 'Public')

    def testGeometryTypeMapped(self):
        r = MitRecord(layer_geom_type_s='Entity point')
        self.assertEqual(r.layer_geom_type_s, 'Point')
