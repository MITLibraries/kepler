# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
import pysolr
import requests

class SolrServiceManager(object):
    def __init__(self, url):
        self.url = url
        self.connection = pysolr.Solr(url)

    def getFromServer(self, query):
        r = requests.get(self.url, data={query:query})
        r.raise_for_status()

    def postMetaDataToServer(self, records):
        for record in records:
            self._validateRecord(record)
        response = self.connection.add(records)
        response.raise_for_status()

    def _validateRecord(self, record):
        if not ('uuid' in record):
            raise AttributeError("missing uuid")