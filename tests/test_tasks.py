# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path

import pytest
import requests_mock
from mock import patch, DEFAULT

from kepler.models import Job, Item
from kepler.tasks import *
from kepler.tasks import (_index_records, _index_from_fgdc, _load_marc_records,
                          _upload_to_geoserver, _fgdc_to_mods)


pytestmark = pytest.mark.usefixtures('app')


@pytest.fixture
def job(db):
    j = Job(item=Item(uri=u'urn:uuid:c8921f5a-eac7-509b-bac5-bd1b2cb202dc',
                      access=u'Public'))
    db.session.add(j)
    return j


@pytest.yield_fixture
def geo_mock():
    with requests_mock.Mocker() as m:
        m.get('/geoserver/rest/imports/0',
              json={'import': {'state': 'COMPLETE'}})
        m.get('/geoserver/rest/imports/1',
              json={'import': {'state': 'WORKING'}})
        yield m


def test_index_shapefile_indexes_from_fgdc(job, bag):
    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms':
        'mock://example.com/geoserver/wms',
        'http://www.opengis.net/def/serviceType/ogc/wfs':
        'mock://example.com/geoserver/wfs',
    }
    with patch('kepler.tasks._index_from_fgdc') as mock:
        index_shapefile(job, bag)
        mock.assert_called_with(job, bag=bag, dct_references_s=refs,
                                uuid='c8921f5a-eac7-509b-bac5-bd1b2cb202dc',
                                layer_id_s='mit:SDE_DATA_BD_A8GNS_2003')


def test_index_shapefile_assigns_layer_id(job, bag):
    with patch('kepler.tasks._index_from_fgdc') as mock:
        index_shapefile(job, bag)
        assert job.item.layer_id == 'mit:SDE_DATA_BD_A8GNS_2003'


def test_index_geotiff_assigns_layer_id(job, bag):
    with patch('kepler.tasks._index_from_fgdc') as mock:
        index_geotiff(job, bag)
        assert job.item.layer_id == 'mit:c8921f5a-eac7-509b-bac5-bd1b2cb202dc'


def test_index_geotiff_indexes_from_fgdc(job, bag):
    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms':
        'mock://example.com/geoserver/wms',
        'http://schema.org/downloadUrl': 'http://example.com/foobar',
    }
    job.item.tiff_url = 'http://example.com/foobar'
    with patch('kepler.tasks._index_from_fgdc') as mock:
        index_geotiff(job, bag)
        mock.assert_called_with(job, bag=bag, dct_references_s=refs,
                                uuid='c8921f5a-eac7-509b-bac5-bd1b2cb202dc',
                                layer_id_s='mit:c8921f5a-eac7-509b-bac5-bd1b2cb202dc')


def test_submit_to_dspace_uploads_sword_package(sword, job, bag_tif):
    submit_to_dspace(job, bag_tif)
    req = sword.request_history[0]
    assert 'X-Packaging' in req.headers
    assert req.text.name.endswith('.zip')


def test_submit_to_dspace_adds_handle_to_item(sword, job, bag_tif):
    submit_to_dspace(job, bag_tif)
    assert job.item.handle == 'mit.edu:dusenbury-device:1'


def test_get_geotiff_url_adds_url_to_item(dspace, job, oai_ore):
    dspace.register_uri('GET', requests_mock.ANY, text=oai_ore)
    job.item.handle = 'http://hdl.handle.net/1234.5/67890'
    get_geotiff_url_from_dspace(job)
    assert job.item.tiff_url == 'http://example.com/bitstream/handle/1234.5/67890/248077.tif?sequence=4'


def test_get_geotiff_url_errors_on_no_tiff(dspace, job, oai_ore_no_tiffs):
    dspace.register_uri('GET', requests_mock.ANY, text=oai_ore_no_tiffs)
    job.item.handle = 'http://hdl.handle.net/1234.5/67890'
    with pytest.raises(Exception) as excinfo:
        get_geotiff_url_from_dspace(job)
    assert 'Expected 1 tiff, found 0' == str(excinfo.value)


def test_get_geotiff_url_errors_on_multiple_tiffs(dspace, job,
                                                  oai_ore_two_tiffs):
    dspace.register_uri('GET', requests_mock.ANY, text=oai_ore_two_tiffs)
    job.item.handle = 'http://hdl.handle.net/1234.5/67890'
    with pytest.raises(Exception) as excinfo:
        get_geotiff_url_from_dspace(job)
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
    db.session.commit()
    resolve_pending_jobs()
    assert job.status == 'PENDING'
    assert job2.status == 'COMPLETED'


def testIndexFromFgdcCreatesRecord(job, bag):
    with patch('kepler.tasks._index_records') as mock:
        _index_from_fgdc(job, bag, layer_id_s='mit:SDE_DATA_BD_A8GNS_2003',
                         uuid='c8921f5a-eac7-509b-bac5-bd1b2cb202dc')
        args = mock.call_args[0]
    assert args[0][0].get('dc_title_s') == 'Bermuda (Geographic Feature Names, 2003)'
    assert args[0][0].get('layer_id_s') == 'mit:SDE_DATA_BD_A8GNS_2003'


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


def testFgdcToModsReturnsMods(bag_tif):
    fgdc = os.path.join(bag_tif, 'data/fgdc.xml')
    mods = _fgdc_to_mods(fgdc)
    assert u'<mods:title>Some land</mods:title>' in mods
