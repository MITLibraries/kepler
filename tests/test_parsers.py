# -*- coding: utf-8 -*-
from __future__ import absolute_import
from io import BytesIO
from xml.etree.ElementTree import Element
from decimal import Decimal, getcontext

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


@pytest.yield_fixture()
def prec_10():
    o_prec = getcontext().prec
    getcontext().prec = 10
    yield
    getcontext().prec = o_prec


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

    def testRecordReturnsRecordAsProcessedDictionary(self, marc):
        parser = MarcParser(marc)
        record = next(iter(parser))
        assert record.get('dc_title_s') == 'Geothermal resources of New Mexico'

    def testRecordReturnsSubjectsAsSet(self, marc):
        parser = MarcParser(marc)
        record = next(iter(parser))
        assert record.get('dct_spatial_sm') == set(['New Mexico', ])

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

    def testConvertCoordConvertsStringToDecimal(self, prec_10):
        degrees = (12 + Decimal(34)/60 + Decimal(56)/3600) * -1
        assert MarcParser.convert_coord("S0123456") == degrees

        degrees = 123 + Decimal('45.6789')/60
        assert MarcParser.convert_coord("12345.6789") == degrees

    def testConvertCoordUsesPrecision(self, prec_10):
        assert MarcParser.convert_coord("12345.6789", precision=5) == Decimal('123.76')

    def testConvertCoordResetsPrecision(self, prec_10):
        MarcParser.convert_coord('12345.6789', precision=2)
        assert Decimal(2)/3 == Decimal('0.6666666667')

    def testConvertCoordReturnsNoneWhenNoMatch(self):
        assert MarcParser.convert_coord("asdf") is None

    def testParsesMarcXml(self, marc):
        parser = MarcParser(marc)
        iparser = iter(parser)
        record = next(iparser)
        assert record['dc_title_s'] == 'Geothermal resources of New Mexico'
