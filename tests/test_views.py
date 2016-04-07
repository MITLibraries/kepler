# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

import pytest
from mock import patch, DEFAULT

from kepler.models import Job, Item


pytestmark = pytest.mark.usefixtures('db')


@pytest.yield_fixture
def geo_tasks():
    patcher = patch.multiple('kepler.layer.views', upload_shapefile=DEFAULT,
                             index_shapefile=DEFAULT, upload_geotiff=DEFAULT,
                             submit_to_dspace=DEFAULT, index_geotiff=DEFAULT)
    yield patcher.start()
    patcher.stop()


@pytest.yield_fixture
def marc_tasks():
    patcher = patch('kepler.marc.views.index_marc_records')
    yield patcher.start()
    patcher.stop()


class TestLayer(object):
    def testReturns201OnSuccess(self, auth_testapp, geo_tasks, bag_upload):
        r = auth_testapp.post('/layers/', upload_files=[('file', bag_upload)])
        assert r.status_code == 201

    def testJobCreated(self, auth_testapp, geo_tasks, bag_upload):
        auth_testapp.post('/layers/', upload_files=[('file', bag_upload)])
        assert Job.query.count() == 1

    def testJobIsRun(self, auth_testapp, geo_tasks, bag_upload):
        auth_testapp.post('/layers/', upload_files=[('file', bag_upload)])
        assert Job.query.first().status == 'COMPLETED'

    def testRunsShapefileTasks(self, auth_testapp, geo_tasks, bag_upload):
        auth_testapp.post('/layers/', upload_files=[('file', bag_upload)])
        assert geo_tasks['upload_shapefile'].called
        assert geo_tasks['index_shapefile'].called

    def testRunsGeotiffTasks(self, auth_testapp, geo_tasks, bag_tif_upload):
        auth_testapp.post('/layers/', upload_files=[('file', bag_tif_upload)])
        assert geo_tasks['upload_geotiff'].called
        assert geo_tasks['submit_to_dspace'].called
        assert geo_tasks['index_geotiff'].called

    def testReturns415OnUnsupportedFormat(self, auth_testapp, geo_tasks,
                                          bag_upload):
        with patch('kepler.layer.views.get_datatype') as datatype:
            datatype.return_value = 'w4rez'
            r = auth_testapp.post('/layers/',
                                  upload_files=[('file', bag_upload)],
                                  expect_errors=True)
        assert r.status_code == 415

    def testReturns401OnNoAuthentication(self, testapp):
        r = testapp.post('/layers/', expect_errors=True)
        assert r.status_code == 401

    def testReturns401OnBadAuthentication(self, testapp):
        testapp.authorization = ('Basic', ('username', 'wat'))
        r = testapp.post('/layers/', expect_errors=True)
        assert r.status_code == 401


class TestMarc(object):
    def testReturns201OnSuccess(self, auth_testapp, marc, marc_tasks):
        r = auth_testapp.post('/marc/', upload_files=[('file', marc)])
        assert r.status_code == 201

    def testJobCreated(self, auth_testapp, marc, marc_tasks):
        auth_testapp.post('/marc/', upload_files=[('file', marc)])
        assert Job.query.count() == 1

    def testJobIsRun(self, auth_testapp, marc, marc_tasks):
        auth_testapp.post('/marc/', upload_files=[('file', marc)])
        assert Job.query.first().status == 'COMPLETED'

    def testReturns401OnNoAuthentication(self, testapp):
        r = testapp.post('/marc/', expect_errors=True)
        assert r.status_code == 401

    def testReturns401OnBadAuthentication(self, testapp):
        testapp.authorization = ('Basic', ('username', 'foobar'))
        r = testapp.post('/marc/', expect_errors=True)
        assert r.status_code == 401


class TestJob(object):
    def testJobRetrievalShowsJob(self, testapp, db):
        job = Job(item=Item(uri=u'TestJob'), status='COMPLETED')
        db.session.add(job)
        db.session.commit()
        r = testapp.get('/%d' % job.id)
        assert 'COMPLETED' in r.text

    def testJobListShowsPendingJobs(self, testapp, db):
        db.session.add(Job(item=Item(uri=u'FOO', layer_id=u'BAR'),
                       status='PENDING'))
        r = testapp.get('/')
        assert 'BAR' in r.text

    def testJobListShowsCompletedJobs(self, testapp, db):
        db.session.add(Job(item=Item(uri=u'FOO', layer_id=u'BAR'),
                       status='COMPLETED'))
        r = testapp.get('/')
        assert 'BAR' in r.text

    def testJobListShowsFailedJobs(self, testapp, db):
        db.session.add(Job(item=Item(uri=u'FOO', layer_id=u'BAR'),
                       status='FAILED'))
        r = testapp.get('/')
        assert 'BAR' in r.text

    def testJobListReturnsOnlyMostRecentJobs(self, testapp, db):
        item = Item(uri=u'Frob')
        db.session.add(Job(item=item, time=datetime(2001, 1, 1)))
        db.session.add(Job(item=item, time=datetime(2002, 1, 1),
                           status="COMPLETED"))
        r = testapp.get('/')
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
