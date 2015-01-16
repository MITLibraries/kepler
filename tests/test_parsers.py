# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tests import unittest
from io import BytesIO
from mock import MagicMock, Mock
from kepler.parsers import parse, FgdcParser, XMLParser

class ParserTestCase(unittest.TestCase):
    def testParseReturnsRecordGenerator(self):
        mock_parser = MagicMock(return_value=range(3))
        records = list(parse(BytesIO(u'foobaz'.encode('utf-8')), mock_parser))
        self.assertEqual(records, [0, 1, 2])


class XMLParserTestCase(unittest.TestCase):
    def testParserYieldsRecordWhenCalled(self):
        parser = XMLParser(BytesIO(u'<record/>'.encode('utf-8')))
        parser.record_elem = 'record'
        records = list(parser)
        self.assertEqual(len(records), 1)

    def testParserCallsHandleElemForElements(self):
        parser = XMLParser(BytesIO(u'<record><title/></record>'.encode('utf-8')))
        parser.record_elem = 'record'
        parser.handle_elem = Mock()
        list(parser)
        self.assertTrue(parser.handle_elem.called)


class FgdcParserTestCase(unittest.TestCase):
    def testHandleElemAddsSelectedFieldsToRecord(self):
        records = list(FgdcParser('tests/data/shapefile/fgdc.xml'))
        self.assertEqual(records[0].get('dc_subject'),
                         ['point', 'names', 'features'])
