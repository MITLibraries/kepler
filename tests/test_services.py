# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
from mock import patch
from flask import current_app

from kepler.services.solr import SolrServiceManager


pytestmark = pytest.mark.usefixtures('app')


@pytest.fixture
def solr():
    return SolrServiceManager(current_app.config['SOLR_URL'])


@pytest.yield_fixture
def pysolr():
    patcher = patch('pysolr.Solr.add')
    yield patcher.start()
    patcher.stop()


class TestSolr(object):
    def testSolrServiceManagerPost(self, pysolr, solr):
        solr.postMetaDataToServer([{'uuid': 'test_uuid'}])
        pysolr.assert_called_once_with([{'uuid': 'test_uuid'}])

    def testValidateRecord(self, solr):
        with pytest.raises(AttributeError):
            self.mgr._validateRecord({'uid': 'test_uuid'})
