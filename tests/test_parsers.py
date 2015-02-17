# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
from tests import unittest
from io import BytesIO
from xml.etree.ElementTree import Element
from mock import MagicMock, Mock
import pymarc
import io
from kepler.parsers import parse, FgdcParser, XMLParser, MarcParser

class ParserTestCase(unittest.TestCase):
    def testParseReturnsRecordGenerator(self):
        mock_parser = MagicMock(return_value=range(3))
        records = list(parse(BytesIO(u'foobaz'.encode('utf-8')), mock_parser))
        self.assertEqual(records, [0, 1, 2])


class XMLParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = XMLParser()
        def start_handler(elem):
            if elem.tag == 'record':
                self.parser.record = {}
        self.parser.record_elem = 'record'
        self.parser.start_handler = Mock(side_effect=start_handler)
        self.parser.end_handler = Mock()

    def testContextReturnsEventElementIterator(self):
        ctx = self.parser._context(BytesIO(u'<record/>'.encode('utf-8')))
        event, elem = next(ctx)
        self.assertEqual(event, 'start')
        self.assertEqual(elem.tag, 'record')

    def testParserYieldsRecordWhenCalled(self):
        self.parser.fstream = BytesIO(u'<record/>'.encode('utf-8'))
        records = list(self.parser)
        self.assertEqual(len(records), 1)

    def testParserCallsStartHandlerForElements(self):
        self.parser.fstream = BytesIO(u'<record><title/></record>'.encode('utf-8'))
        list(self.parser)
        self.assertEqual(self.parser.start_handler.call_count, 2)

    def testParserCallsEndHandlerForElements(self):
        self.parser.fstream = BytesIO(u'<record><title/></record>'.encode('utf-8'))
        list(self.parser)
        self.assertEqual(self.parser.end_handler.call_count, 2)


class FgdcParserTestCase(unittest.TestCase):
    def setUp(self):
        metadata = io.open('tests/data/shapefile/fgdc.xml', encoding='utf-8')
        parser = FgdcParser(metadata)
        self.record = next(iter(parser))

    def testStartHandlerCreatesEmptyDictionary(self):
        parser = FgdcParser()
        parser.start_handler(Element(FgdcParser.record_elem))
        self.assertEqual(parser.record, {})

    def testParserAddsSelectedFieldsToRecord(self):
        self.assertEqual(self.record['dc_title_s'],
                         'Bermuda (Geographic Feature Names, 2003)')

    def testParserReturnsThemeKeywordsAsSet(self):
        self.assertEqual(self.record['dc_subject_sm'],
                         set(['point', 'names', 'features']))

    def testParserReturnsSpatialKeywordsAsSet(self):
        self.assertEqual(self.record['dct_spatial_sm'], set(['Bermuda']))

    def testParserReturnsCreatorsAsSet(self):
        self.assertEqual(self.record['dc_creator_sm'],
                         set(['National Imagery and Mapping Agency']))


class MarcParserTestCase(unittest.TestCase):
    MARC_NS = 'http://www.loc.gov/MARC21/slim'

    def testStartHandlerCreatesMarcRecord(self):
        parser = MarcParser()
        parser.start_handler(Element(MarcParser.record_elem))
        self.assertIsInstance(parser._record, pymarc.Record)

    def testStartHandlerSetsCurrentDataField(self):
        parser = MarcParser()
        parser.start_handler(Element('{%s}datafield' % self.MARC_NS,
                                     attrib={'tag': '245'}))
        self.assertEqual(parser._field.tag, '245')

    def testStartHandlerSetsCurrentControlField(self):
        parser = MarcParser()
        el = Element('{%s}controlfield' % self.MARC_NS, attrib={'tag': '001'})
        el.text = '000002579'
        parser.start_handler(el)
        self.assertEqual(parser._field.tag, '001')

    def testEndHandlerAddsCurrentDataFieldToRecord(self):
        parser = MarcParser()
        parser._record = pymarc.Record()
        el = Element('{%s}datafield' % self.MARC_NS, attrib={'tag': '245'})
        parser.start_handler(el)
        parser.end_handler(el)
        self.assertEqual(len(parser._record.get_fields('245')), 1)

    def testEndHandlerAddsCurrentControlFieldToRecord(self):
        parser = MarcParser()
        parser._record = pymarc.Record()
        el = Element('{%s}controlfield' % self.MARC_NS, attrib={'tag': '001'})
        el.text = '000002579'
        parser.start_handler(el)
        parser.end_handler(el)
        self.assertEqual(parser._record['001'].value(), el.text)

    def testEndHandlerAddsSubFieldToCurrentDataField(self):
        parser = MarcParser()
        parser._field = pymarc.Field('245', indicators=[1,0])
        el = Element('{%s}subfield' % self.MARC_NS, attrib={'code': 'a'})
        el.text = 'The Locations of Frobbers in the Greater Boston Area'
        parser.end_handler(el)
        self.assertEqual(parser._field.get_subfields('a'), [el.text])

    def testRecordReturnsRecordAsProcessedDictionary(self):
        parser = MarcParser()
        record = pymarc.Record()
        field = pymarc.Field('245', indicators=[1, 0])
        field.add_subfield('a', 'The Locations of Frobbers:')
        field.add_subfield('b', 'Greater Boston Area')
        record.add_field(field)
        parser._record = record
        self.assertEqual(parser.record.get('dc_title'),
                         'The Locations of Frobbers: Greater Boston Area')

    def testRecordReturnsSubjectsAsList(self):
        parser = MarcParser()
        record = pymarc.Record()
        field = pymarc.Field('650', indicators=[0, 0])
        field.add_subfield('z', 'This')
        field.add_subfield('z', 'is')
        field.add_subfield('z', 'kittentown')
        record.add_field(field)
        parser._record = record
        self.assertEqual(parser.record.get('dct_spatial'),
                         ['This', 'is', 'kittentown'])

    def testCoordRegexExtractsPartsOfCoordinate(self):
        parts = MarcParser.COORD_REGEX.search("N0123456")
        self.assertEqual(parts.groupdict().get('hemisphere'), 'N')
        self.assertEqual(parts.groupdict().get('degrees'), '012')
        self.assertEqual(parts.groupdict().get('minutes'), '34')
        self.assertEqual(parts.groupdict().get('seconds'), '56')

        parts = MarcParser.COORD_REGEX.search("e123.456789")
        self.assertEqual(parts.groupdict().get('hemisphere'), 'e')
        self.assertEqual(parts.groupdict().get('degrees'), '123.456789')

        parts = MarcParser.COORD_REGEX.search("-123.456789")
        self.assertEqual(parts.groupdict().get('hemisphere'), '-')
        self.assertEqual(parts.groupdict().get('degrees'), '123.456789')

        parts = MarcParser.COORD_REGEX.search("S12345.6789")
        self.assertEqual(parts.groupdict().get('hemisphere'), 'S')
        self.assertEqual(parts.groupdict().get('degrees'), '123')
        self.assertEqual(parts.groupdict().get('minutes'), '45.6789')

        parts = MarcParser.COORD_REGEX.search("W1234567.89")
        self.assertEqual(parts.groupdict().get('hemisphere'), 'W')
        self.assertEqual(parts.groupdict().get('degrees'), '123')
        self.assertEqual(parts.groupdict().get('minutes'), '45')
        self.assertEqual(parts.groupdict().get('seconds'), '67.89')

    def testConvertCoordConvertsStringToDecimal(self):
        degrees = 12 + 34/60 + 56/3600
        self.assertAlmostEqual(MarcParser.convert_coord("S0123456"), -degrees)

        degrees = 123 + 45.6789/60
        self.assertAlmostEqual(MarcParser.convert_coord("12345.6789"), degrees)

    def testParsesMarcXml(self):
        parser = MarcParser('tests/data/marc.xml')
        iparser = iter(parser)
        record = next(iparser)
        self.assertEqual(record['dc_title'],
                         'Geothermal resources of New Mexico')
