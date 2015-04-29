# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
from io import BytesIO
from xml.etree.ElementTree import Element

import pytest
from mock import Mock
import pymarc

from kepler.parsers import XMLParser, MarcParser


@pytest.fixture
def parser():
    fp = BytesIO(u'<record><title/></record>'.encode('utf-8'))
    parser = XMLParser(fp)

    def start_handler(elem):
        if elem.tag == 'record':
            parser.record = {}
    parser.record_elem = 'record'
    parser.start_handler = Mock(side_effect=start_handler)
    parser.end_handler = Mock()
    return parser


def almost_equal(x, y):
    return abs(x - y) <= 0.0000001


class TestXMLParser(object):
    def testContextReturnsEventElementIterator(self, parser):
        event, elem = next(parser._context(parser.fstream))
        assert event == 'start'
        assert elem.tag == 'record'

    def testParserYieldsRecordWhenCalled(self, parser):
        records = list(parser)
        assert len(records) == 1

    def testParserCallsStartHandlerForElements(self, parser):
        list(parser)
        assert parser.start_handler.call_count == 2

    def testParserCallsEndHandlerForElements(self, parser):
        list(parser)
        assert parser.end_handler.call_count == 2


class TestMarcParser(object):
    MARC_NS = 'http://www.loc.gov/MARC21/slim'

    def testStartHandlerCreatesMarcRecord(self):
        parser = MarcParser()
        parser.start_handler(Element(MarcParser.record_elem))
        assert isinstance(parser._record, pymarc.Record)

    def testStartHandlerSetsCurrentDataField(self):
        parser = MarcParser()
        parser.start_handler(Element('{%s}datafield' % self.MARC_NS,
                                     attrib={'tag': '245'}))
        assert parser._field.tag == '245'

    def testStartHandlerSetsCurrentControlField(self):
        parser = MarcParser()
        el = Element('{%s}controlfield' % self.MARC_NS, attrib={'tag': '001'})
        el.text = '000002579'
        parser.start_handler(el)
        assert parser._field.tag == '001'

    def testEndHandlerAddsCurrentDataFieldToRecord(self):
        parser = MarcParser()
        parser._record = pymarc.Record()
        el = Element('{%s}datafield' % self.MARC_NS, attrib={'tag': '245'})
        parser.start_handler(el)
        parser.end_handler(el)
        assert len(parser._record.get_fields('245')) == 1

    def testEndHandlerAddsCurrentControlFieldToRecord(self):
        parser = MarcParser()
        parser._record = pymarc.Record()
        el = Element('{%s}controlfield' % self.MARC_NS, attrib={'tag': '001'})
        el.text = '000002579'
        parser.start_handler(el)
        parser.end_handler(el)
        assert parser._record['001'].value() == el.text

    def testEndHandlerAddsSubFieldToCurrentDataField(self):
        parser = MarcParser()
        parser._field = pymarc.Field('245', indicators=[1, 0])
        el = Element('{%s}subfield' % self.MARC_NS, attrib={'code': 'a'})
        el.text = 'The Locations of Frobbers in the Greater Boston Area'
        parser.end_handler(el)
        assert parser._field.get_subfields('a') == [el.text]

    def testRecordReturnsRecordAsProcessedDictionary(self):
        parser = MarcParser()
        record = pymarc.Record()
        field = pymarc.Field('245', indicators=[1, 0])
        field.add_subfield('a', 'The Locations of Frobbers:')
        field.add_subfield('b', 'Greater Boston Area')
        record.add_field(field)
        parser._record = record
        assert parser.record.get('dc_title') == \
            'The Locations of Frobbers: Greater Boston Area'

    def testRecordReturnsSubjectsAsList(self):
        parser = MarcParser()
        record = pymarc.Record()
        field = pymarc.Field('650', indicators=[0, 0])
        field.add_subfield('z', 'This')
        field.add_subfield('z', 'is')
        field.add_subfield('z', 'kittentown')
        record.add_field(field)
        parser._record = record
        assert parser.record.get('dct_spatial') == ['This', 'is', 'kittentown']

    def testCoordRegexExtractsPartsOfCoordinate(self):
        parts = MarcParser.COORD_REGEX.search("N0123456")
        assert parts.groupdict().get('hemisphere') == 'N'
        assert parts.groupdict().get('degrees') == '012'
        assert parts.groupdict().get('minutes') == '34'
        assert parts.groupdict().get('seconds') == '56'

        parts = MarcParser.COORD_REGEX.search("e123.456789")
        assert parts.groupdict().get('hemisphere') == 'e'
        assert parts.groupdict().get('degrees') == '123.456789'

        parts = MarcParser.COORD_REGEX.search("-123.456789")
        assert parts.groupdict().get('hemisphere') == '-'
        assert parts.groupdict().get('degrees') == '123.456789'

        parts = MarcParser.COORD_REGEX.search("S12345.6789")
        assert parts.groupdict().get('hemisphere') == 'S'
        assert parts.groupdict().get('degrees') == '123'
        assert parts.groupdict().get('minutes') == '45.6789'

        parts = MarcParser.COORD_REGEX.search("W1234567.89")
        assert parts.groupdict().get('hemisphere') == 'W'
        assert parts.groupdict().get('degrees') == '123'
        assert parts.groupdict().get('minutes') == '45'
        assert parts.groupdict().get('seconds') == '67.89'

    def testConvertCoordConvertsStringToDecimal(self):
        degrees = 12 + 34/60 + 56/3600
        assert almost_equal(MarcParser.convert_coord("S0123456"), -degrees)

        degrees = 123 + 45.6789/60
        assert almost_equal(MarcParser.convert_coord("12345.6789"), degrees)

    def testParsesMarcXml(self):
        parser = MarcParser('tests/data/marc.xml')
        iparser = iter(parser)
        record = next(iparser)
        assert record['dc_title'] == 'Geothermal resources of New Mexico'
