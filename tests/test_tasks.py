# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
import os.path
import re

import arrow
import pytest
import requests_mock
from mock import patch, DEFAULT

from kepler.models import Job, Item
from kepler.tasks import *
from kepler.tasks import (_index_records, _load_marc_records,
                          _prep_solr_record, _upload_to_geoserver,
                          _fgdc_to_mods)


pytestmark = pytest.mark.usefixtures('app')


@pytest.fixture
def job(db):
    j = Job(item=Item(uri=u'urn:uuid:c8921f5a-eac7-509b-bac5-bd1b2cb202dc',
                      access=u'Public'))
    db.session.add(j)
    return j


@pytest.yield_fixture
def geo_mock():
    r = re.compile('/geoserver/rest/imports/.*')
    with requests_mock.Mocker() as m:
        m.get('/geoserver/rest/imports/0', json={
            'import': {
                'state': 'COMPLETE',
                'tasks': [{
                    'href': 'mock://example.com/geoserver/rest/imports/0/tasks/0'}]
            }
        })
        m.get('/geoserver/rest/imports/1',
              json={'import': {'state': 'WORKING'}})
        m.get('/geoserver/rest/imports/2', status_code=404)
        m.get('/geoserver/rest/imports/3',
              json={'import': {'state': 'PENDING',
                    'tasks': [{'state': 'NO_CRS'}]}})
        m.delete(r)
        m.post(re.compile('mock://localhost:8983/solr/.*'))
        yield m


def test_index_shapefile_stores_record(job, bag):
    index_shapefile(job, bag)
    assert json.loads(job.item.record).get('layer_id_s') == \
        'mit:SDE_DATA_BD_A8GNS_2003'


def test_index_shapefile_assigns_layer_id(job, bag):
    index_shapefile(job, bag)
    assert job.item.layer_id == 'mit:SDE_DATA_BD_A8GNS_2003'


def test_index_geotiff_assigns_layer_id(job, bag_tif):
    index_geotiff(job, bag_tif)
    assert job.item.layer_id == 'mit:grayscale'


def test_index_geotiff_indexes_from_fgdc(job, bag_tif):
    job.item.tiff_url = 'http://example.com/foobar'
    index_geotiff(job, bag_tif)
    assert json.loads(job.item.record).get('layer_id_s') == 'mit:grayscale'


def test_submit_to_dspace_uploads_sword_package(sword, job, bag_tif):
    submit_to_dspace(job, bag_tif)
    req = sword.request_history[0]
    assert 'X-Packaging' in req.headers
    assert req.text.name.endswith('.zip')


def test_submit_to_dspace_adds_handle_to_item(sword, job, bag_tif):
    submit_to_dspace(job, bag_tif)
    assert job.item.handle == 'mit.edu:dusenbury-device:1'


def test_get_geotiff_url_adds_url_to_item(dspace, job, oai_ore, bag):
    dspace.register_uri('GET', requests_mock.ANY, text=oai_ore)
    job.item.handle = 'http://hdl.handle.net/1234.5/67890'
    get_geotiff_url_from_dspace(job, bag)
    assert job.item.tiff_url == 'http://example.com/bitstream/handle/1234.5/67890/248077.tif?sequence=4'


def test_get_geotiff_url_errors_on_no_tiff(dspace, job, oai_ore_no_tiffs, bag):
    dspace.register_uri('GET', requests_mock.ANY, text=oai_ore_no_tiffs)
    job.item.handle = 'http://hdl.handle.net/1234.5/67890'
    with pytest.raises(Exception) as excinfo:
        get_geotiff_url_from_dspace(job, bag)
    assert 'Expected 1 tiff, found 0' == str(excinfo.value)


def test_get_geotiff_url_errors_on_multiple_tiffs(dspace, job,
                                                  oai_ore_two_tiffs, bag):
    dspace.register_uri('GET', requests_mock.ANY, text=oai_ore_two_tiffs)
    job.item.handle = 'http://hdl.handle.net/1234.5/67890'
    with pytest.raises(Exception) as excinfo:
        get_geotiff_url_from_dspace(job, bag)
    assert 'Expected 1 tiff, found 2' == str(excinfo.value)


def test_does_not_submit_to_dspace_with_existing_handle(sword, job, bag_tif):
    job.item.handle = "popcorn"
    submit_to_dspace(job, bag_tif)
    assert not sword.called


def testSubmitToDspaceWithExistingHandleDoesNotChangeHandle(job, bag_tif):
    job.item.handle = "popcorn"
    submit_to_dspace(job, bag_tif)
    assert job.item.handle == "popcorn"


def test_upload_shapefile_sets_import_url(job, bag, geoserver):
    upload_shapefile(job, bag)
    assert job.import_url == 'mock://example.com/geoserver/rest/imports/0'


def test_upload_geotiff_sets_import_url(job, bag_tif, geoserver):
    upload_geotiff(job, bag_tif)
    assert job.import_url == 'mock://example.com/geoserver/rest/imports/0'


def testUploadGeotiffCompressesTiff(job, bag_tif, geoserver):
    with patch.multiple('kepler.tasks', compress=DEFAULT,
                        pyramid=DEFAULT) as mocks:
        upload_geotiff(job, bag_tif)
        assert mocks['compress'].called


def testUploadGeotiffPyramidsTiff(job, bag_tif, geoserver):
    with patch.multiple('kepler.tasks', pyramid=DEFAULT) as mocks:
        upload_geotiff(job, bag_tif)
        assert mocks['pyramid'].called


def test_resolve_pending_completes_finished_imports(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/0'
    job.status = 'PENDING'
    job.item.record = '{"uuid": "foo"}'
    db.session.commit()
    resolve_pending_jobs()
    assert job.status == 'COMPLETED'


def test_resolve_pending_skips_unfinished_imports(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/1'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    assert job.status == 'PENDING'


def test_resolve_pending_resolves_only_last_job_for_item(job, db, geo_mock):
    job.status = 'PENDING'
    job2 = Job(item=job.item, status='PENDING')
    db.session.add(job2)
    job.import_url = 'mock://example.com/geoserver/rest/imports/0'
    job2.import_url = 'mock://example.com/geoserver/rest/imports/0'
    job.item.record = '{"uuid": "FOO"}'
    db.session.commit()
    resolve_pending_jobs()
    assert job.status == 'PENDING'
    assert job2.status == 'COMPLETED'


def test_resolve_pending_fails_jobs_with_exceptions(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/2'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    assert job.status == 'FAILED'


def test_resolve_pending_records_exception(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/2'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    assert 'HTTPError: 404' in job.error_msg


def test_resolve_pending_fails_jobs_for_failed_import_tasks(job, db,
                                                            geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/3'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    assert job.status == 'FAILED'


def test_resolve_pending_deletes_finished_jobs(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/0'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    assert geo_mock.request_history.pop().method == 'DELETE'


def test_resolve_pending_deletes_tasks_in_import(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/0'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    task_req = geo_mock.request_history[-2]
    assert task_req.method == 'DELETE'
    assert 'imports/0/tasks/0' in task_req.url


def test_resolve_pending_does_not_delete_pending_jobs(job, db, geo_mock):
    job.import_url = 'mock://example.com/geoserver/rest/imports/1'
    job.status = 'PENDING'
    db.session.commit()
    resolve_pending_jobs()
    assert geo_mock.request_history.pop().method == 'GET'


def test_publish_record_adds_record_to_solr(db, job):
    job.item.record = '{"layer_id_s": "mit:FOOBARBAZ"}'
    db.session.commit()
    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY)
        publish_record(job.id)
        req = m.request_history[0]
    assert '<doc><field name="layer_id_s">mit:FOOBARBAZ</field></doc>' in \
        req.text


def test_publish_record_sets_status(db, job):
    job.item.record = '{"uuid": "foobar"}'
    db.session.commit()
    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY)
        publish_record(job.id)
    assert job.status == 'COMPLETED'


def test_publish_record_fails_record_on_error(db, job):
    job.item.record = '{"uuid": "foobar"}'
    db.session.commit()
    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, status_code=500)
        publish_record(job.id)
    assert job.status == 'FAILED'


def test_upload_to_geoserver_uploads_data(geoserver, shapefile):
    _upload_to_geoserver(shapefile, 'shapefile', 'public', 'test')
    assert geoserver.call_count == 4


def test_upload_to_geoserver_uses_correct_url(geoserver, shapefile):
    _upload_to_geoserver(shapefile, 'shapefile', 'restricted', 'test')
    req = geoserver.request_history[0]
    assert req.url.startswith('mock://secure.example.com/geoserver')


def testIndexRecordsAddsRecordsToSolr(pysolr):
    _index_records([{'uuid': 'foobar'}])
    req = pysolr.request_history[0]
    assert '<doc><field name="uuid">foobar</field></doc>' in req.text


def testIndexRecordsConvertsSets(pysolr):
    _index_records([{'dc_creator_s': set(['Foo', 'Bar'])}])
    req = pysolr.request_history[0]
    assert '<field name="dc_creator_s">Foo</field>' in req.text
    assert '<field name="dc_creator_s">Bar</field>' in req.text


@pytest.mark.skip()
def testLoadMarcRecordsReturnsRecordIterator(marc):
    records = _load_marc_records(marc)
    assert next(records).get('dc_title_s') == 'Geothermal resources of New Mexico'


@pytest.mark.skip()
def testIndexMarcRecordsIndexesRecords(job, marc):
    with patch('kepler.tasks._index_records') as mock:
        index_marc_records(job, marc)
        args = mock.call_args[0]
    assert next(args[0]).get('dc_title_s') == 'Geothermal resources of New Mexico'


@pytest.mark.skip()
def testLoadMarcRecordsCreatesUuid(marc):
    records = _load_marc_records(marc)
    assert next(records).get('uuid') == 'cb41c773-9570-5feb-8bac-ea6203d1541e'


def testFgdcToModsReturnsMods(bag_tif):
    fgdc = os.path.join(bag_tif, 'data/fgdc.xml')
    mods = _fgdc_to_mods(fgdc)
    assert u'<mods:title>Some land</mods:title>' in mods


def test_prep_solr_record_converts_dates():
    now = arrow.now()
    rec = _prep_solr_record({'foo': now})
    assert rec['foo'] == now.to('utc').format('YYYY-MM-DDTHH:mm:ss') + 'Z'
