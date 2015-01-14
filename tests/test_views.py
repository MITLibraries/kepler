# -*- coding: utf-8 -*-
from __future__ import absolute_import
from mock import patch
from tests import BaseTestCase
from kepler.extensions import db
from kepler.exceptions import UnsupportedFormat
from kepler.models import Job

class IngestTestCase(BaseTestCase):
    def setUp(self):
        super(IngestTestCase, self).setUp()
        self.upload_files = [
            ('shapefile', "tests/data/shapefile/shapefile.zip"),
            ('metadata', "tests/data/shapefile/fgdc.xml")
        ]

    @patch('requests.put')
    def testIngestPostReturns202OnSuccess(self, req):
        r = self.app.post('/ingest/', upload_files=self.upload_files)
        self.assertEqual(r.status_code, 202)

    def testIngestCreatesJob(self):
        with patch('kepler.ingest.views.create_job') as mock:
            instance = mock.return_value
            self.app.post('/ingest/', upload_files=self.upload_files)
            self.assertTrue(instance.run.called)

    def testIngestReturns415OnUnsupportedFormatError(self):
        with patch('kepler.ingest.views.create_job') as mock:
            mock.side_effect = UnsupportedFormat('application/example')
            r = self.app.post('/ingest/', upload_files=self.upload_files,
                              expect_errors=True)
            self.assertEqual(r.status_code, 415)

    @patch('requests.put')
    def testIngestCompletesJobOnSuccess(self, req):
        with patch('kepler.jobs.UploadJob.complete') as mock:
            self.app.post('/ingest/', upload_files=self.upload_files)
            self.assertTrue(mock.called)

    def testIngestFailsJobOnError(self):
        self.app.app.debug = False
        with patch('kepler.ingest.views.create_job') as mock:
            instance = mock.return_value
            instance.run.side_effect = AttributeError()
            try:
                self.app.post('/ingest/', upload_files=self.upload_files,
                              expect_errors=True)
            except AttributeError:
                pass
            self.assertTrue(instance.fail.called)

    def testIngestReturns500OnJobRunError(self):
        self.app.app.debug = False
        self.app.app.config['PROPAGATE_EXCEPTIONS'] = False
        with patch('kepler.ingest.views.create_job') as mock:
            instance = mock.return_value
            instance.run.side_effect = AttributeError()
            r = self.app.post('/ingest/', upload_files=self.upload_files,
                              expect_errors=True)
            self.assertEqual(r.status_code, 500)

    def testGetIngestReturns200OnSuccess(self):
        job = Job(name=u'TestJob')
        db.session.add(job)
        db.session.commit()
        r = self.app.get('/ingest/%s' % job.name)
        self.assertEqual(r.status_code, 200)

    def testGetIngestReturnsJob(self):
        job = Job(name=u'TestJob')
        db.session.add(job)
        db.session.commit()
        r = self.app.get('/ingest/%s' % job.name)
        self.assertEqual(r.json['id'], job.id)
