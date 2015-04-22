# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io

from mock import patch, Mock

from tests import BaseTestCase
from kepler.models import Job
from kepler.jobs import create_job, JobRunner, job_completed, job_failed
from kepler.exceptions import UnsupportedFormat


class JobFactoryTestCase(BaseTestCase):
    def setUp(self):
        super(JobFactoryTestCase, self).setUp()
        self.data = io.open('tests/data/bermuda.zip', 'rb')

    def tearDown(self):
        super(JobFactoryTestCase, self).tearDown()
        self.data.close()

    def testCreatesJob(self):
        create_job(u'shapefile', u'LEURENT', self.data)
        self.assertEqual(Job.query.count(), 1)

    def testJobIsCreatedWithPendingStatus(self):
        create_job(u'shapefile', u'RUMBLUS', self.data)
        job = Job.query.first()
        self.assertEqual(job.status, 'PENDING')

    def testReturnsShapefileJobRunner(self):
        job = create_job(u'shapefile', u'KHOLER', self.data)
        self.assertIsInstance(job, JobRunner)

    def testReturnsGeotiffJobRunner(self):
        job = create_job(u'geotiff', u'ALPHARD', self.data)
        self.assertIsInstance(job, JobRunner)

    def testSetsFailedStatusOnError(self):
        with patch('kepler.jobs.JobRunner', side_effect=Exception):
            try:
                create_job(u'shapefile', u'FROST', self.data)
            except Exception:
                pass
            self.assertEqual(Job.query.first().status, u'FAILED')

    def testReRaisesExceptions(self):
        with patch('kepler.jobs.JobRunner', side_effect=KeyError):
            with self.assertRaises(KeyError):
                create_job(u'shapefile', u'MALRONA', self.data)

    def testRaisesUnsupportedFormatError(self):
        with self.assertRaises(UnsupportedFormat):
            create_job(u'warez', u'BLOODY_VICTORIA', self.data)


class JobRunnerTestCase(BaseTestCase):
    def setUp(self):
        super(JobRunnerTestCase, self).setUp()
        self.job = Job(name=u'FOO', status=u'PENDING')

    def testCompletedSignalSentOnSuccess(self):
        run = JobRunner(Mock(), self.job)
        with patch('kepler.jobs.job_completed.send') as mock:
            run()
        self.assertEqual(mock.call_count, 1)

    def testFailedSignalSentOnError(self):
        run = JobRunner(Mock(side_effect=Exception), self.job)
        with patch('kepler.jobs.job_failed.send') as mock:
            try:
                run()
            except Exception:
                pass
        self.assertEqual(mock.call_count, 1)

    def testExceptionReRaisedOnFailure(self):
        run = JobRunner(Mock(side_effect=KeyError), self.job)
        with self.assertRaises(KeyError):
            run()


class JobSignalsTestCase(BaseTestCase):
    def setUp(self):
        super(JobSignalsTestCase, self).setUp()
        self.job = Job(name=u'FOO', status=u'PENDING')

    def testCompletedSetsCompletedStatus(self):
        job_completed.send(Mock(job=self.job))
        self.assertEqual(self.job.status, u'COMPLETED')

    def testFailedSetsFailedStatus(self):
        job_failed.send(Mock(job=self.job))
        self.assertEqual(self.job.status, u'FAILED')
