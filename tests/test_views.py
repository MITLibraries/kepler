# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

import pytest
from mock import patch

from kepler.models import Job, Item


@pytest.yield_fixture
def create_job():
    patcher = patch('kepler.job.views.create_job')
    yield patcher.start()
    patcher.stop()


class TestJob(object):
    def testJobCreationReturns201OnSuccess(self, testapp, create_job):
        r = testapp.post('/jobs/', {'uri': 'foobar', 'type': 'shapefile'},
                         upload_files=[('file', 'tests/data/bermuda.zip')])
        assert r.status_code == 201

    def testJobCreationRunsJob(self, testapp, create_job):
        testapp.post('/jobs/', {'uri': 'foobar', 'type': 'shapefile'},
                     upload_files=[('file', 'tests/data/bermuda.zip')])
        assert create_job.call_count == 1

    def testJobCreationReturns500OnJobRunError(self, testapp, create_job):
        create_job.side_effect = Exception
        testapp.app.debug = False
        testapp.app.config['PROPAGATE_EXCEPTIONS'] = False
        r = testapp.post('/jobs/', {'uri': 'foobar', 'type': 'shapefile'},
                         upload_files=[('file', 'tests/data/bermuda.zip')],
                         expect_errors=True)
        assert r.status_code == 500

    def testJobCreationReturns415OnUnsupportedFormat(self, testapp, db):
        r = testapp.post('/jobs/', {'uri': 'foobar', 'type': 'warez'},
                         expect_errors=True)
        assert r.status_code == 415

    def testJobRetrievalShowsJob(self, testapp, db):
        job = Job(item=Item(uri=u'TestJob'), status='COMPLETED')
        db.session.add(job)
        db.session.commit()
        r = testapp.get('/jobs/%d' % job.id)
        assert 'COMPLETED' in r.text

    def testJobListReturnsJobs(self, testapp, db):
        db.session.add(Job(item=Item(uri=u'FOO')))
        db.session.add(Job(item=Item(uri=u'BAR')))
        r = testapp.get('/jobs/')
        assert 'FOO' in r.text
        assert 'BAR' in r.text

    def testJobListReturnsOnlyMostRecentJobs(self, testapp, db):
        item = Item(uri=u'Frob')
        db.session.add(Job(item=item, time=datetime(2001, 1, 1)))
        db.session.add(Job(item=item, time=datetime(2002, 1, 1),
                           status="COMPLETED"))
        r = testapp.get('/jobs/')
        assert 'COMPLETED' in r.text
        assert 'PENDING' not in r.text


class TestItem(object):
    def testItemListReturnsItems(self, testapp, db):
        db.session.add_all([Item(uri=u'Foo'), Item(uri=u'Bar')])
        db.session.commit()
        r = testapp.get('/items/')
        assert 'Foo' in r.text
        assert 'Bar' in r.text

    def testItemRetrievalShowsItem(self, testapp, db):
        item = Item(uri=u'Foobar')
        db.session.add(item)
        db.session.commit()
        r = testapp.get('/items/%s' % item.id)
        assert 'Foobar' in r.text
