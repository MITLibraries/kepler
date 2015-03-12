# -*- coding: utf-8 -*-
from __future__ import absolute_import
from mock import patch, Mock, DEFAULT
import io
from requests.exceptions import HTTPError
from werkzeug.datastructures import FileStorage
from tests import BaseTestCase
from kepler.jobs import (create_job, UploadJob, ShapefileUploadJob,
                         GeoTiffUploadJob,)
from kepler.extensions import db
from kepler.models import Job
from kepler.exceptions import UnsupportedFormat

class JobTestCase(BaseTestCase):
    def setUp(self):
        super(JobTestCase, self).setUp()
        self.data = Mock()
        self.data.filename = u'TestFile'
        self.data.mimetype = 'application/zip'


class JobFactoryTestCase(JobTestCase):
    def testCreateJobCreatesJob(self):
        create_job(u'LEURENT', self.data)
        self.assertEqual(Job.query.count(), 1)

    def testJobIsCreatedWithPendingStatus(self):
        create_job(u'RUMBLUS', self.data)
        job = Job.query.first()
        self.assertEqual(job.status, 'PENDING')

    def testCreateJobReturnsJob(self):
        job = create_job(u'KHOLER', self.data)
        self.assertIsInstance(job, UploadJob)

    def testCreateJobCreatesShapefileJobFromMimetype(self):
        job = create_job(u'ALPHARD', self.data)
        self.assertIsInstance(job, ShapefileUploadJob)

    def testCreateJobCreatesGeoTiffJobFromMimetype(self):
        self.data.mimetype = 'image/tiff'
        job = create_job(u'LUPI', self.data)
        self.assertIsInstance(job, GeoTiffUploadJob)

    def testCreateJobSetsFailedStatusOnError(self):
        with patch('kepler.jobs.ShapefileUploadJob') as mock:
            mock.side_effect = Exception
            try:
                create_job(u'FROST', self.data)
            except:
                pass
            self.assertEqual(Job.query.first().status, 'FAILED')

    def testCreateJobReRaisesExceptions(self):
        with patch('kepler.jobs.ShapefileUploadJob') as mock:
            mock.side_effect = AttributeError()
            with self.assertRaises(AttributeError):
                create_job(u'MALRONA', self.data)

    def testCreateJobRaisesUnsupportedFormat(self):
        self.data.mimetype = 'application/example'
        with self.assertRaises(UnsupportedFormat):
            create_job(u'BLOODY_VICTORIA', self.data)


class UploadJobTestCase(JobTestCase):
    def testFailSetsFailedStatus(self):
        job = Job(name=None, status=u'PENDING')
        db.session.add(job)
        db.session.commit()
        uploadjob = UploadJob(job, data=None)
        uploadjob.fail()
        self.assertEqual(Job.query.first().status, 'FAILED')

    def testCompleteSetsCompletedStatus(self):
        job = Job(name=None, status=u'PENDING')
        db.session.add(job)
        db.session.commit()
        uploadjob = UploadJob(job, data=None)
        uploadjob.complete()
        self.assertEqual(Job.query.first().status, 'COMPLETED')

    def testRunMethodRaisesNotImplementedError(self):
        with self.assertRaises(NotImplementedError):
            job = UploadJob(job=None, data=None)
            job.run()


class ShapefileUploadJobTestCase(BaseTestCase):
    def setUp(self):
        super(ShapefileUploadJobTestCase, self).setUp()
        self.data_stream = io.open('tests/data/shapefile/shapefile.zip', 'rb')
        self.data = FileStorage(self.data_stream, 'test_shapefile',
                                content_type='application/zip')
        self.metadata = io.open('tests/data/shapefile/fgdc.xml',
                                encoding='utf-8')
        self.job = ShapefileUploadJob(Job(name=u'test_shapefile'), self.data,
                                      self.metadata)

    def tearDown(self):
        super(ShapefileUploadJobTestCase, self).tearDown()
        self.data_stream.close()
        self.metadata.close()

    @patch('requests.put')
    @patch('pysolr.Solr.add')
    def testRunUploadsShapefileToGeoserver(self, mock_solr, mock_geoserver):
        self.job.run()
        mock_geoserver.assert_called_with(
            'http://example.com/geoserver/rest/workspaces/mit/datastores/data/file.shp',
            data=self.data, headers={'Content-type': 'application/zip'})

    @patch('requests.put')
    @patch('pysolr.Solr.add')
    def testRunUploadsMetadataToSolr(self, mock_solr, mock_geoserver):
        self.job.run()
        records = mock_solr.call_args[0]
        self.assertEqual(records[0][0]['layer_id_s'], 'mit:test_shapefile')

    @patch('pysolr.Solr.add')
    @patch.multiple('requests', put=DEFAULT, delete=DEFAULT)
    def testDeletesFromGeoServerWhenSolrErrors(self, mock_solr, delete, put):
        attrs = {'raise_for_status.side_effect': HTTPError}
        mock_solr.return_value = Mock(**attrs)
        try:
            self.job.run()
        except HTTPError:
            pass
        delete.assert_called_once_with(
                'http://example.com/geoserver/rest/workspaces/mit/datastores/data/featuretypes/test_shapefile?recurse=true')

    @patch('pysolr.Solr.add')
    @patch.multiple('requests', put=DEFAULT, delete=DEFAULT)
    def testReraisesErrorAfterCleaningUp(self, mock_solr, delete, put):
        attrs = {'raise_for_status.side_effect': HTTPError}
        mock_solr.return_value = Mock(**attrs)
        with self.assertRaises(HTTPError):
            self.job.run()


class GeoTiffUploadJobTestCase(BaseTestCase):
    def setUp(self):
        super(GeoTiffUploadJobTestCase, self).setUp()
        self.data_stream = io.open('tests/data/rgb.tif', 'rb')
        self.data = FileStorage(self.data_stream, 'test_geotiff',
                                content_type='image/tiff')
        self.metadata = io.open('tests/data/shapefile/fgdc.xml',
                                encoding='utf-8')
        self.job = GeoTiffUploadJob(Job(name=u'test_geotiff'), self.data,
                                      self.metadata)

    def tearDown(self):
        super(GeoTiffUploadJobTestCase, self).tearDown()
        self.data_stream.close()
        self.metadata.close()

    @patch('requests.put')
    @patch('kepler.jobs.SolrServiceManager')
    def testUploadsRasterToGeoServer(self, mock_solr, mock_geoserver):
        self.job.run()
        mock_geoserver.assert_called_with(
            'http://example.com/geoserver/rest/workspaces/mit/coveragestores/test_geotiff/file.geotiff',
            data=self.data, headers={'Content-type': 'image/tiff'})

    @patch('kepler.jobs.SolrServiceManager', side_effect=HTTPError)
    @patch.multiple('requests', put=DEFAULT, delete=DEFAULT)
    def testDeletesFromGeoServerWhenSolrErrors(self, mock_solr, delete, put):
        try:
            self.job.run()
        except HTTPError:
            pass
        delete.assert_called_once_with(
            'http://example.com/geoserver/rest/workspaces/mit/coveragestores/test_geotiff?recurse=true')
