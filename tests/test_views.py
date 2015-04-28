# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

from mock import patch

from tests import BaseTestCase
from kepler.extensions import db
from kepler.models import Job, Item


class JobTestCase(BaseTestCase):
    @patch('kepler.job.views.create_job')
    def testJobCreationReturns201OnSuccess(self, mock):
        r = self.app.post('/job/', {'uuid': 'foobar', 'type': 'shapefile'},
                          upload_files=[('file', 'tests/data/bermuda.zip')])
        self.assertEqual(r.status_code, 201)

    @patch('kepler.job.views.create_job')
    def testJobCreationRunsJob(self, mock):
        self.app.post('/job/', {'uuid': 'foobar', 'type': 'shapefile'},
                      upload_files=[('file', 'tests/data/bermuda.zip')])
        self.assertEqual(mock.call_count, 1)

    @patch('kepler.job.views.create_job', side_effect=Exception)
    def testJobCreationReturns500OnJobRunError(self, mock):
        self.app.app.debug = False
        self.app.app.config['PROPAGATE_EXCEPTIONS'] = False
        r = self.app.post('/job/', {'uuid': 'foobar', 'type': 'shapefile'},
                          upload_files=[('file', 'tests/data/bermuda.zip')],
                          expect_errors=True)
        self.assertEqual(r.status_code, 500)

    def testJobCreationReturns415OnUnsupportedFormat(self):
        r = self.app.post('/job/', {'uuid': 'foobar', 'type': 'warez'},
                          expect_errors=True)
        self.assertEqual(r.status_code, 415)

    def testJobRetrievalReturns200OnSuccess(self):
        job = Job(item=Item(uri=u'TestJob'))
        db.session.add(job)
        r = self.app.get('/job/%s' % job.item.uri)
        self.assertEqual(r.status_code, 200)

    def testJobRetrievalReturnsMostRecentJob(self):
        item = Item(uri=u'TestJob')
        db.session.add(Job(item=item, time=datetime(2001, 1, 1)))
        db.session.add(Job(item=item, status="COMPLETED",
                           time=datetime(2002, 1, 1)))
        r = self.app.get('/job/TestJob')
        self.assertEqual(r.json['status'], 'COMPLETED')

    def testJobListReturnsJobs(self):
        db.session.add(Job(item=Item(uri=u'FOO')))
        db.session.add(Job(item=Item(uri=u'BAR')))
        r = self.app.get('/job/')
        self.assertIn('FOO', r.text)
        self.assertIn('BAR', r.text)

    def testJobListReturnsOnlyMostRecentJobs(self):
        item = Item(uri=u'Frob')
        db.session.add(Job(item=item, time=datetime(2001, 1, 1)))
        db.session.add(Job(item=item, time=datetime(2002, 1, 1),
                           status="COMPLETED"))
        r = self.app.get('/job/')
        self.assertIn('COMPLETED', r.text)
        self.assertNotIn('PENDING', r.text)
