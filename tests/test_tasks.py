# -*- coding: utf-8 -*-
from __future__ import absolute_import
import tempfile
import shutil
import os.path

import git
import pytest
from mock import Mock, patch

from kepler.tasks import *


pytestmark = pytest.mark.usefixtures('app')


@pytest.yield_fixture
def repo(testapp):
    remote_dir = tempfile.mkdtemp()
    local = tempfile.mkdtemp()
    remote = os.path.join(remote_dir, 'repo')
    shutil.copytree('tests/fixtures/repo', remote)
    r = git.Repo.init(remote)
    r.index.add('*')
    r.index.commit("Baby's first commit")
    testapp.app.config['OGM_REPOSITORIES'] = dict([(remote, local)])
    yield remote
    shutil.rmtree(remote_dir)
    shutil.rmtree(local)


class TestTasks(object):
    @patch('kepler.tasks.put')
    def testUploadToGeoserverUploadsData(self, mock):
        record, data = Mock(_filename='foo'), Mock()
        upload_to_geoserver(record, data, 'application/shp')
        mock.assert_called_once_with('foo', data, 'application/shp')

    def testIndexRecordAddsRecordToSolr(self, pysolr_add):
        record = Mock()
        record.as_dict = Mock(return_value={'uuid': 'foobar'})
        index_record(record)
        pysolr_add.assert_called_once_with([{'uuid': 'foobar'}])

    def testMakeRecordCreatesNewRecord(self, bag):
        record, data = make_record(Mock(), bag)
        assert record.dc_title_s == u'Bermuda (Geographic Feature Names, 2003)'

    def testLoadRepoRecordsReturnsRecordsIterator(self, repo):
        records = load_repo_records(repo)
        assert next(records) == {"layer_id_s": "FOOBAR"}

    def testIndexRecordsAddsRecordsToSolr(self, pysolr_add):
        records = [{'uuid': 'foobar'}, {'uuid': 'foobaz'}]
        index_records(records)
        pysolr_add.assert_called_once_with(records)
