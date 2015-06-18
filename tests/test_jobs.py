# -*- coding: utf-8 -*-
from __future__ import absolute_import

from mock import patch, Mock
import pytest

from kepler.models import Job, Item
from kepler.jobs import create_job, JobRunner, job_completed, job_failed
from kepler.exceptions import UnsupportedFormat


pytestmark = pytest.mark.usefixtures('db')


@pytest.fixture
def job():
    return Job(item=Item(uri=u'FOO'), status=u'PENDING')


class TestJobFactory(object):
    def testCreatesItem(self, bag):
        create_job({'type': u'shapefile', 'uri': u'SEAMUS'}, bag)
        assert Item.query.count() == 1

    def testSetsAccessLevel(self, bag):
        form = {'type': u'shapefile', 'uri': u'FOO', 'access': u'Restricted'}
        create_job(form, bag)
        assert Item.query.first().access == u'Restricted'

    def testCreatesJob(self, bag):
        create_job({'type': u'shapefile', 'uri': u'LEURENT'}, bag)
        assert Job.query.count() == 1

    def testJobIsCreatedWithPendingStatus(self, bag):
        create_job({'type': u'shapefile', 'uri': u'RUMBLUS'}, bag)
        job = Job.query.first()
        assert job.status == u'PENDING'

    def testReturnsShapefileJobRunner(self, bag):
        job = create_job({'type': u'shapefile', 'uri': u'KHOLER'}, bag)
        assert isinstance(job, JobRunner)

    def testReturnsGeotiffJobRunner(self, bag):
        job = create_job({'type': u'geotiff', 'uri': u'ALPHARD'}, bag)
        assert isinstance(job, JobRunner)

    def testSetsFailedStatusOnError(self, bag):
        with patch('kepler.jobs.JobRunner', side_effect=Exception):
            try:
                create_job({'type': u'shapefile', 'uri': u'FROST'}, bag)
            except Exception:
                pass
            assert Job.query.first().status == u'FAILED'

    def testReRaisesExceptions(self, bag):
        with patch('kepler.jobs.JobRunner', side_effect=KeyError):
            with pytest.raises(KeyError):
                create_job({'type': u'shapefile', 'uri': u'MALRONA'}, bag)

    def testRaisesUnsupportedFormatError(self, bag):
        with pytest.raises(UnsupportedFormat):
            create_job({'type': u'warez', 'uri': u'BLOODY_VICTORIA'}, bag)


class TestJobRunner(object):
    def testCompletedSignalSentOnSuccess(self, job, bag):
        run = JobRunner(job, bag, [Mock()])
        with patch('kepler.jobs.job_completed.send') as mock:
            run()
        assert mock.call_count == 1

    def testFailedSignalSentOnError(self, job, bag):
        run = JobRunner(job, bag, [Mock(side_effect=Exception)])
        with patch('kepler.jobs.job_failed.send') as mock:
            try:
                run()
            except Exception:
                pass
        assert mock.call_count == 1

    def testExceptionReRaisedOnFailure(self, job, bag):
        run = JobRunner(job, bag, [Mock(side_effect=KeyError)])
        with pytest.raises(KeyError):
            run()


class TestJobSignals(object):
    def testCompletedSetsCompletedStatus(self, job):
        job_completed.send(Mock(job=job))
        assert job.status == u'COMPLETED'

    def testFailedSetsFailedStatus(self, job):
        job_failed.send(Mock(job=job))
        assert job.status == u'FAILED'
