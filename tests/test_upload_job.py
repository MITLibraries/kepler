# -*- coding: utf-8 -*-
from __future__ import absolute_import
from mock import patch, Mock
import io
from flask import current_app
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
        create_job(self.data)
        self.assertEqual(Job.query.count(), 1)

    def testJobIsCreatedWithPendingStatus(self):
        create_job(self.data)
        job = Job.query.first()
        self.assertEqual(job.status, 'PENDING')

    def testCreateJobReturnsJob(self):
        job = create_job(self.data)
        self.assertIsInstance(job, UploadJob)

    def testCreateJobCreatesShapefileJobFromMimetype(self):
        job = create_job(self.data)
        self.assertIsInstance(job, ShapefileUploadJob)

    def testCreateJobCreatesGeoTiffJobFromMimetype(self):
        self.data.mimetype = 'image/tiff'
        job = create_job(self.data)
        self.assertIsInstance(job, GeoTiffUploadJob)

    def testCreateJobSetsFailedStatusOnError(self):
        with patch('kepler.jobs.ShapefileUploadJob') as mock:
            mock.side_effect = Exception
            try:
                create_job(self.data)
            except:
                pass
            self.assertEqual(Job.query.first().status, 'FAILED')

    def testCreateJobReRaisesExceptions(self):
        with patch('kepler.jobs.ShapefileUploadJob') as mock:
            mock.side_effect = AttributeError()
            with self.assertRaises(AttributeError):
                create_job(self.data)

    def testCreateJobRaisesUnsupportedFormat(self):
        self.data.mimetype = 'application/example'
        with self.assertRaises(UnsupportedFormat):
            create_job(self.data)


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


class ShapefileUploadJobTestCase(JobTestCase):
    @patch('requests.put')
    def testRunUploadsShapefileToGeoserver(self, mock):
        url = current_app.config['GEOSERVER_URL']
        file = io.BytesIO(u'Test file'.encode('utf-8'))
        job = ShapefileUploadJob(job=Job(), data=file)
        job.run()
        mock.assert_called_with(url, file)

    def testCreateRecordReturnsMetadataRecord(self):
        data = io.open('tests/data/shapefile/shapefile.zip', 'rb')
        metadata = io.open('tests/data/shapefile/fgdc.xml', encoding='utf-8')
        job = ShapefileUploadJob(job=Job(), data=data)
        self.assertEqual(job.create_record(metadata).get('dc_title'),
                         'Bermuda (Geographic Feature Names, 2003)')
