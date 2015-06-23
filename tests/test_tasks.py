# -*- coding: utf-8 -*-
from __future__ import absolute_import
import tempfile
import shutil
import os.path

import git
import pytest
from mock import Mock, patch

from kepler.tasks import *
from kepler.tasks import (_index_records, _index_from_fgdc, _load_marc_records,
                          _upload_to_geoserver, _load_repo_records)


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


@pytest.fixture
def job():
    j = Mock()
    j.item.uri = 'urn:uuid:c8921f5a-eac7-509b-bac5-bd1b2cb202dc'
    j.item.access = 'public'
    return j


def testIndexShapefileIndexesFromFGDC(job, bag):
    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms': 'http://example.com/geoserver/wms',
        'http://www.opengis.net/def/serviceType/ogc/wfs': 'http://example.com/geoserver/wfs',
    }
    with patch('kepler.tasks._index_from_fgdc') as mock:
        index_shapefile(job, bag)
        mock.assert_called_with(job, bag=bag, dct_references_s=refs)


def testIndexGeotiffIndexesFromFGDC(job, bag):
    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms': 'http://example.com/geoserver/wms',
        'http://schema.org/downloadUrl': 'http://example.com/foobar',
    }
    job.item.handle = 'http://example.com/foobar'
    with patch('kepler.tasks._index_from_fgdc') as mock:
        index_geotiff(job, bag)
        mock.assert_called_with(job, bag=bag, dct_references_s=refs)


def testIndexRepoRecordsIndexesRecords(job):
    with patch('kepler.tasks._index_records') as mock:
        with patch('kepler.tasks._load_repo_records') as repo:
            repo.return_value = 'foobar'
            index_repo_records(job, 'foo/bar')
            mock.assert_called_with('foobar')


def testSubmitToDspaceUploadsSwordPackage(job, bag):
    with patch('kepler.tasks.sword.submit') as mock:
        submit_to_dspace(job, bag)
        mock.assert_called


def testSubmitToDspaceAddsHandleToItem(job, bag):
    with patch('kepler.tasks.sword.submit') as mock:
        mock.return_value = 'foobar'
        submit_to_dspace(job, bag)
        assert job.item.handle == 'foobar'


def testUploadShapefileCallsUploadWithMimetype(job, bag):
    with patch('kepler.tasks._upload_to_geoserver') as mock:
        upload_shapefile(job, bag)
        mock.assert_called_with(job, bag=bag, mimetype='application/zip')


def testUploadGeotiffCallsUploadWithMimetype(job, bag):
    with patch('kepler.tasks._upload_to_geoserver') as mock:
        upload_geotiff(job, bag)
        mock.assert_called_with(job, bag=bag, mimetype='image/tiff')


def testIndexFromFgdcCreatesRecord(job, bag):
    with patch('kepler.tasks._index_records') as mock:
        _index_from_fgdc(job, bag)
        args = mock.call_args[0]
    assert args[0][0].get('dc_title_s') == 'Bermuda (Geographic Feature Names, 2003)'


def testIndexFromFgdcAddsLayerId(job, bag):
    with patch('kepler.tasks._index_records') as mock:
        _index_from_fgdc(job, bag)
        args = mock.call_args[0]
    assert args[0][0].get('layer_id_s') == 'mit:c8921f5a-eac7-509b-bac5-bd1b2cb202dc'


def testIndexFromFgdcAddsUuid(job, bag):
    with patch('kepler.tasks._index_records') as mock:
        _index_from_fgdc(job, bag)
        args = mock.call_args[0]
    assert args[0][0].get('uuid') == 'c8921f5a-eac7-509b-bac5-bd1b2cb202dc'


def testUploadToGeoserverUploadsData(job, bag, shapefile):
    with patch('kepler.tasks.put') as mock:
        _upload_to_geoserver(job, bag, 'application/zip')
    mock.assert_called_once_with('http://example.com/geoserver/', job.item.uri,
                                 shapefile, 'application/zip')


def testUploadToGeoServerUsesCorrectUrl(job, bag, shapefile):
    with patch('kepler.tasks.put') as mock:
        job.access = 'Restricted'
        _upload_to_geoserver(job, bag, 'application/zip')
    assert mock.call_args[0][0] == 'http://example.com/secure-geoserver/'


def testIndexRecordsAddsRecordsToSolr(pysolr_add):
    _index_records([{'uuid': 'foobar'}])
    pysolr_add.assert_called_once_with([{'uuid': 'foobar'}])


def testLoadRepoRecordsReturnsRecordsIterator(repo):
    records = _load_repo_records(repo)
    assert next(records) == {"layer_id_s": "FOOBAR"}


def testLoadMarcRecordsReturnsRecordIterator(marc):
    records = _load_marc_records(marc)
    assert next(records).get('dc_title_s') == 'Geothermal resources of New Mexico'


def testIndexMarcRecordsIndexesRecords(job, marc):
    with patch('kepler.tasks._index_records') as mock:
        index_marc_records(job, marc)
        args = mock.call_args[0]
    assert next(args[0]).get('dc_title_s') == 'Geothermal resources of New Mexico'


def testLoadMarcRecordsCreatesUuid(marc):
    records = _load_marc_records(marc)
    assert next(records).get('uuid') == 'cb41c773-9570-5feb-8bac-ea6203d1541e'
