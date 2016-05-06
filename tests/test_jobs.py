# -*- coding: utf-8 -*-
from __future__ import absolute_import
import tempfile
import uuid

from mock import patch, Mock
import pytest

from kepler.models import Job, Item
from kepler.jobs import create_job, JobRunner, job_completed, job_failed


pytestmark = pytest.mark.usefixtures('db')


@pytest.fixture
def job(db):
    j = Job(item=Item(uri=u'FOO'), status=u'PENDING')
    db.session.add(j)
    db.session.commit()
    return j


class TestJobFactory(object):
    def testCreatesItem(self, bag):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        create_job(uid.urn, bag, [Mock()], 'Public')
        assert Item.query.count() == 1

    def testCreatesJob(self, bag):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        create_job(uid.urn, bag, [Mock()], 'Public')
        assert Job.query.count() == 1

    def testJobCreatedAsPending(self, bag):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        create_job(uid.urn, bag, [Mock()], 'Public')
        assert Job.query.first().status == 'PENDING'

    def testSetsFailedStatusOnError(self, bag):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        with patch('kepler.jobs.JobRunner', side_effect=Exception):
            try:
                create_job(uid.urn, bag, [Mock()], 'Public')
            except Exception:
                pass
            assert Job.query.first().status == u'FAILED'

    def testReRaisesExceptions(self, bag):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        with patch('kepler.jobs.JobRunner', side_effect=KeyError):
            with pytest.raises(KeyError):
                create_job(uid.urn, bag, [Mock()], 'Public')


class TestJobRunner(object):
    def testCompletedSignalSentOnSuccess(self, job):
        run = JobRunner(job.id, tempfile.mkdtemp(), [Mock()])
        with patch('kepler.jobs.job_completed.send') as mock:
            run()
        assert mock.call_count == 1

    def testFailedSignalSentOnError(self, job):
        run = JobRunner(job.id, tempfile.mkdtemp(),
                        [Mock(side_effect=Exception)])
        with patch('kepler.jobs.job_failed.send') as mock:
            try:
                run()
            except Exception:
                pass
        assert mock.call_count == 1

    def testExceptionReRaisedOnFailure(self, job):
        run = JobRunner(job.id, tempfile.mkdtemp(),
                        [Mock(side_effect=KeyError)])
        with pytest.raises(KeyError):
            run()


class TestJobSignals(object):
    def testCompletedSetsCompletedStatus(self, job):
        job_completed.send(JobRunner(job.id, tempfile.mkdtemp(), []), job=job)
        assert job.status == u'COMPLETED'

    def testFailedSetsFailedStatus(self, job):
        job_failed.send(JobRunner(job.id, tempfile.mkdtemp(), []), job=job)
        assert job.status == u'FAILED'
