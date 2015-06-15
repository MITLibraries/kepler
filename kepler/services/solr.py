# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pysolr


class SolrServiceManager(object):
    """Service to a GeoBlacklight (Solr) instance

    :param str url: url to solr database
    """
    def __init__(self, url):
        self.url = url
        self.connection = pysolr.Solr(url)

    def getFromServer(self, query):
        pass

    def postMetaDataToServer(self, records):
        """Post one or more records to solr instance

        :param list records: list of metadata objects
        :raises HTTPError: when solr returns 404, 500, etc.
        """
        for record in records:
            self._validateRecord(record)
        self.connection.add(records)

    def _validateRecord(self, record):
        """Validate metadata record to match solr config

        :param dict record: metadata object
        :raises AttributeError: when missing required key
        """
        if not ('uuid' in record):
            raise AttributeError("missing uuid")
