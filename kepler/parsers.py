# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
try:
    from lxml.etree import iterparse
except ImportError:
    from xml.etree.ElementTree import iterparse
import pymarc
import re


class XMLParser(object):
    """Base streaming XML parser for iterating over records.

    A subclass must implement ``start_handler`` and ``end_handler`` methods that
    accept an Element. The subclass must also provide an attribute called
    ``record_elem`` that specifies the element name for a record. This is a
    namespace aware parser, so make sure to include the namespace if one exists.

    :param fstream: file name or file object
    :returns: record generator
    """

    def __init__(self, fstream=None):
        self.fstream = fstream

    def __iter__(self):
        for event, elem in self._context(self.fstream):
            if event == 'start':
                self.start_handler(elem)
            else:
                if elem.tag == self.record_elem:
                    self.end_handler(elem)
                    yield self.record
                else:
                    self.end_handler(elem)
                elem.clear()

    def _context(self, fstream):
        return iterparse(fstream, events=('start', 'end'))


class MarcParser(XMLParser):
    MARC_NS = 'http://www.loc.gov/MARC21/slim'
    record_elem = '{http://www.loc.gov/MARC21/slim}record'

    ###################
    # MARC lists the following possible formats for a coordinate in the 034
    # field:
    #   hdddmmss
    #   hddd.dddddd
    #   [+/-]ddd.dddddd (plus sign optional)
    #   hdddmm.mmmm
    #   hdddmmss.sss
    ###################
    COORD_REGEX = re.compile(
        r"""^(?P<hemisphere>[NSEW+-])?
             (?P<degrees>\d{3}(\.\d*)?)
             (?P<minutes>\d{2}(\.\d*)?)?
             (?P<seconds>\d{2}(\.\d*)?)?""", re.IGNORECASE|re.VERBOSE)

    def start_handler(self, elem):
        if elem.tag == self.record_elem:
            self._record = pymarc.Record()
        elif elem.tag == '{%s}datafield' % self.MARC_NS:
            tag = elem.get('tag')
            ind1 = elem.get('ind1')
            ind2 = elem.get('ind2')
            self._field = pymarc.Field(tag, indicators=[ind1, ind2])
        elif elem.tag == '{%s}controlfield' % self.MARC_NS:
            if elem.get('tag').isdigit(): # skip controlfields that are letters
                self._field = pymarc.Field(elem.get('tag'))

    def end_handler(self, elem):
        if elem.tag == '{%s}datafield' % self.MARC_NS:
            self._record.add_field(self._field)
            self._field = None
        elif elem.tag == '{%s}controlfield' % self.MARC_NS:
            if elem.get('tag').isdigit():
                self._field.data = elem.text
                self._record.add_field(self._field)
                self._field = None
        elif elem.tag == '{%s}subfield' % self.MARC_NS:
            self._field.add_subfield(elem.get('code'), elem.text)

    @property
    def record(self):
        record = {}
        record['dc_title'] = self._record.title()
        record['dc_publisher'] = self._record.publisher()
        record['dc_creator'] = self._record.author()
        if '520' in self._record:
            record['dc_description'] = self._record['520'].format_field()
        for field in self._record.get_fields('650'):
            for subfield in field.get_subfields('a'):
                record.setdefault('dc_subject', []).append(subfield)
            for subfield in field.get_subfields('z'):
                record.setdefault('dct_spatial', []).append(subfield)
        record['dct_temporal'] = self._record.pubyear()
        if '876' in self._record:
            record['_datatype'] = self._record['876']['k']
            record['_location'] = self._record['876']['B']
        record['_marc_id'] = self._record['001']
        if '034' in self._record:
            record['_bbox_w'] = self._record['034']['d']
            record['_bbox_e'] = self._record['034']['e']
            record['_bbox_n'] = self._record['034']['f']
            record['_bbox_s'] = self._record['034']['g']
        return record

    @classmethod
    def convert_coord(cls, coordinate):
        matches = cls.COORD_REGEX.search(coordinate)
        if not matches:
            return None
        parts = matches.groupdict()
        decimal = float(parts.get('degrees')) + \
                  float(parts.get('minutes') or 0) / 60 + \
                  float(parts.get('seconds') or 0) / 3600
        if parts.get('hemisphere') and parts.get('hemisphere').lower() in 'ws-':
            decimal = -decimal
        return decimal
