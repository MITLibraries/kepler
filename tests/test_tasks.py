# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path

import pytest
import requests
import requests_mock
from mock import Mock, patch, DEFAULT

from kepler.tasks import *
from kepler.tasks import (_index_records, _index_from_fgdc, _load_marc_records,
                          _upload_to_geoserver, _fgdc_to_mods)


pytestmark = pytest.mark.usefixtures('app')


@pytest.fixture
def job():
    j = Mock()
    j.item.handle = None
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


def testSubmitToDspaceUploadsSwordPackage(job, bag_tif):
    with patch('kepler.tasks.sword.submit') as mock:
        submit_to_dspace(job, bag_tif)
        assert mock.called


def testSubmitToDspaceAddsHandleToItem(job, bag_tif):
    with patch('kepler.tasks.sword.submit') as mock:
        mock.return_value = 'foobar'
        submit_to_dspace(job, bag_tif)
        assert job.item.handle == 'foobar'


def testGetGeotiffUrlFromDspaceAddsGeotiffUrlToItem(job, oai_ore):
    with requests_mock.mock() as m:
        m.get('http://example.com/metadata/handle/1234.5/67890/ore.xml',
              text=oai_ore)
        job.item.handle = 'http://hdl.handle.net/1234.5/67890'
        get_geotiff_url_from_dspace(job)
        assert job.item.tiff_url == 'http://example.com/bitstream/handle/1234.5/67890/248077.tif?sequence=4'


def testGetGeotiffUrlFromDspaceErrorsOnNoTiffs(job, oai_ore_no_tiffs):
    with requests_mock.mock() as m:
        m.get('http://example.com/metadata/handle/1234.5/67890/ore.xml',
              text=oai_ore_no_tiffs)
        job.item.handle = 'http://hdl.handle.net/1234.5/67890'
        with pytest.raises(Exception) as excinfo:
            get_geotiff_url_from_dspace(job)
        assert 'Expected 1 tiff, found 0' == str(excinfo.value)


def testGetGeotiffUrlFromDspaceErrorsOnMultipleTiffs(job, oai_ore_two_tiffs):
    with requests_mock.mock() as m:
        m.get('http://example.com/metadata/handle/1234.5/67890/ore.xml',
              text=oai_ore_two_tiffs)
        job.item.handle = 'http://hdl.handle.net/1234.5/67890'
        with pytest.raises(Exception) as excinfo:
            get_geotiff_url_from_dspace(job)
        assert 'Expected 1 tiff, found 2' == str(excinfo.value)


def testSubmitToDspaceWithExistingHandleDoesNotSubmit(job, bag_tif):
    job.item.handle = "popcorn"
    with patch('kepler.tasks.sword.submit') as mock:
        submit_to_dspace(job, bag_tif)
        assert not mock.called


def testSubmitToDspaceWithExistingHandleDoesNotChangeHandle(job, bag_tif):
    job.item.handle = "popcorn"
    submit_to_dspace(job, bag_tif)
    assert job.item.handle == "popcorn"


def testUploadShapefileCallsUploadWithMimetype(job, bag, shapefile):
    with patch('kepler.tasks._upload_to_geoserver') as mock:
        upload_shapefile(job, bag)
        kwargs = mock.call_args[1]
        assert kwargs['mimetype'] == 'application/zip'


def testUploadGeotiffCallsUploadWithMimetype(job, bag_tif):
    with patch('kepler.tasks._upload_to_geoserver') as mock:
        upload_geotiff(job, bag_tif)
        kwargs = mock.call_args[1]
        assert kwargs['mimetype'] == 'image/tiff'


def testUploadGeotiffCompressesTiff(job, bag_tif):
    with patch.multiple('kepler.tasks', _upload_to_geoserver=DEFAULT,
                        compress=DEFAULT, pyramid=DEFAULT) as mocks:
        upload_geotiff(job, bag_tif)
        assert mocks['compress'].called


def testUploadGeotiffPyramidsTiff(job, bag_tif):
    with patch.multiple('kepler.tasks', _upload_to_geoserver=DEFAULT,
                        pyramid=DEFAULT) as mocks:
        upload_geotiff(job, bag_tif)
        assert mocks['pyramid'].called


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


def testUploadToGeoserverUploadsData(job, shapefile):
    with patch('kepler.tasks.put') as mock:
        _upload_to_geoserver(job, shapefile, 'application/zip')
    mock.assert_called_once_with('http://example.com/geoserver/', job.item.uri,
                                 shapefile, 'application/zip')


def testUploadToGeoServerUsesCorrectUrl(job, bag, shapefile):
    with patch('kepler.tasks.put') as mock:
        job.item.access = 'Restricted'
        _upload_to_geoserver(job, bag, 'application/zip')
    assert mock.call_args[0][0] == 'http://example.com/secure-geoserver/'


def testUploadToGeoServerSetsLayerId(job, bag, shapefile, db):
    with patch('kepler.tasks.put') as mock:
        mock.return_value = 'foo:bar'
        _upload_to_geoserver(job, bag, 'application/zip')
    assert job.item.layer_id == 'foo:bar'


def testIndexRecordsAddsRecordsToSolr(pysolr):
    pysolr.register_uri(requests_mock.ANY, requests_mock.ANY)
    _index_records([{'uuid': 'foobar'}])
    req = pysolr.request_history[0]
    assert '<doc><field name="uuid">foobar</field></doc>' in req.text


def testIndexRecordsConvertsSets(pysolr):
    pysolr.register_uri(requests_mock.ANY, requests_mock.ANY)
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
