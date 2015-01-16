# -*- coding: utf-8 -*-
from __future__ import absolute_import
try:
    from lxml.etree import iterparse
except ImportError:
    from xml.etree.ElementTree import iterparse

def parse(fstream, parser):
    return parser(fstream)


class XMLParser(object):
    def __init__(self, fstream):
        self.context = iterparse(fstream)
        self.record = {}

    def __iter__(self):
        for event, elem in self.context:
            if elem.tag == self.record_elem:
                record = self.record
                self.record = {}
                yield record
            else:
                self.handle_elem(elem)
            elem.clear()


class FgdcParser(XMLParser):
    record_elem = 'metadata'

    def handle_elem(self, elem):
        if elem.tag == 'title':
            self.record['dc_title'] = elem.text
        elif elem.tag == 'origin':
            self.record['dc_creator'] = elem.text
        elif elem.tag == 'abstract':
            self.record['dc_description'] = elem.text
        elif elem.tag == 'publish':
            self.record['dc_publisher'] = elem.text
        elif elem.tag == 'westbc':
            self.record['_bbox_w'] = elem.text
        elif elem.tag == 'eastbc':
            self.record['_bbox_e'] = elem.text
        elif elem.tag == 'northbc':
            self.record['_bbox_n'] = elem.text
        elif elem.tag == 'southbc':
            self.record['_bbox_s'] = elem.text
        elif elem.tag == 'accconst':
            self.record['dc_rights'] = elem.text
        elif elem.tag == 'themekey':
            self.record.setdefault('dc_subject', []).append(elem.text)
        elif elem.tag == 'placekey':
            self.record.setdefault('dct_spatial', []).append(elem.text)

