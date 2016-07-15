# -*- coding: utf-8 -*-
from __future__ import absolute_import
import filecmp
import tempfile
import uuid

from mock import patch, Mock
import pytest

from kepler.models import Job, Item
from kepler.jobs import create_job, fetch_bag, run_job, delete_bag


pytestmark = pytest.mark.usefixtures('db')


@pytest.fixture
def job(db):
    j = Job(item=Item(uri=u'd2fe4762-96ec-57cd-89c9-312ec097284b'),
            status=u'CREATED')
    db.session.add(j)
    db.session.commit()
    return j


class TestJobFactory(object):
    def testCreatesItem(self):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        create_job(uid.urn)
        assert Item.query.count() == 1

    def testCreatesJob(self):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        create_job(uid.urn)
        assert Job.query.count() == 1

    def testJobCreatedAsCreated(self):
        uid = uuid.UUID('d2fe4762-96ec-57cd-89c9-312ec097284b')
        create_job(uid.urn)
        assert Job.query.first().status == 'CREATED'


def test_fetch_bag_returns_file_name(s3, bag_upload):
    s3.client.upload_file(bag_upload, 'test_bucket', 'test_bag')
    fname = fetch_bag('test_bucket', 'test_bag')
    assert filecmp.cmp(fname, bag_upload)


def test_run_job_sets_status_to_pending(s3, job, bag_upload, pysolr,
                                        geoserver):
    s3.client.upload_file(bag_upload, 'test_bucket', 'd2fe4762-96ec-57cd-89c9-312ec097284b')
    run_job(job.id)
    assert job.status == 'PENDING'


def test_run_job_removes_bag_from_s3(s3, job, bag_upload, pysolr, geoserver):
    s3.client.upload_file(bag_upload, 'test_bucket', 'd2fe4762-96ec-57cd-89c9-312ec097284b')
    run_job(job.id)
    keys = s3.client.list_objects_v2(Bucket='test_bucket')
    assert 'Contents' not in keys


def test_delete_bag_deletes_bag(s3, bag_upload):
    s3.client.upload_file(bag_upload, 'test_bucket', 'test_bag')
    delete_bag('test_bucket', 'test_bag')
    keys = s3.client.list_objects_v2(Bucket='test_bucket')
    assert 'Contents' not in keys
