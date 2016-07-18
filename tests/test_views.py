# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

import pytest

from kepler.models import Job, Item


pytestmark = pytest.mark.usefixtures('db', 'pysolr', 'sword', 'geoserver')


@pytest.fixture
def item_with_job(db):
    job = Job(item=Item(uri='d2fe4762-96ec-57cd-89c9-312ec097284b'),
              status='CREATED')
    db.session.add(job)
    db.session.commit()


class TestLayer(object):
    def testReturns201OnSuccess(self, s3, auth_testapp, bag_upload):
        s3.client.upload_file(bag_upload, 'test_bucket',
                              'd2fe4762-96ec-57cd-89c9-312ec097284b')
        r = auth_testapp.put('/layers/d2fe4762-96ec-57cd-89c9-312ec097284b')
        assert r.status_code == 201

    def testShapefileJobIsRun(self, s3, auth_testapp, bag_upload):
        s3.client.upload_file(bag_upload, 'test_bucket',
                              'd2fe4762-96ec-57cd-89c9-312ec097284b')
        auth_testapp.put('/layers/d2fe4762-96ec-57cd-89c9-312ec097284b')
        assert Job.query.first().status == 'PENDING'

    def testTiffJobIsRun(self, s3, auth_testapp, bag_tif_upload):
        s3.client.upload_file(bag_tif_upload, 'test_bucket',
                              '674a0ab1-325f-561a-a837-09e9a9a79b91')
        auth_testapp.put('/layers/674a0ab1-325f-561a-a837-09e9a9a79b91')
        assert Job.query.first().status == 'PENDING'

    def testReturns401OnNoAuthentication(self, testapp):
        r = testapp.put('/layers/674a0ab1-325f-561a-a837-09e9a9a79b91',
                        expect_errors=True)
        assert r.status_code == 401

    def testReturns401OnBadAuthentication(self, testapp):
        testapp.authorization = ('Basic', ('username', 'wat'))
        r = testapp.put('/layers/674a0ab1-325f-561a-a837-09e9a9a79b91',
                        expect_errors=True)
        assert r.status_code == 401

    def test_get_returns_200(self, item_with_job, auth_testapp):
        r = auth_testapp.get('/layers/d2fe4762-96ec-57cd-89c9-312ec097284b')
        assert r.status_code == 200

    def test_get_returns_json_with_conneg(self, item_with_job, auth_testapp):
        r = auth_testapp.get('/layers/d2fe4762-96ec-57cd-89c9-312ec097284b',
                             headers={'accept': 'application/json'})
        assert r.json == {'uri': 'd2fe4762-96ec-57cd-89c9-312ec097284b',
                          'status': 'CREATED'}

    def test_get_returns_json_with_extension(self, item_with_job,
                                             auth_testapp):
        r = auth_testapp.get(
                '/layers/d2fe4762-96ec-57cd-89c9-312ec097284b.json')
        assert r.json == {'uri': 'd2fe4762-96ec-57cd-89c9-312ec097284b',
                          'status': 'CREATED'}


class xTestMarc(object):
    def testReturns201OnSuccess(self, auth_testapp, marc):
        r = auth_testapp.post('/marc/', upload_files=[('file', marc)])
        assert r.status_code == 201

    def testJobIsRun(self, auth_testapp, marc):
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

    def test_job_shows_layer_id(self, testapp, db):
        job = Job(item=Item(uri='674a0ab1-325f-561a-a837-09e9a9a79b91',
                            layer_id='mit:Foobar'))
        db.session.add(job)
        db.session.commit()
        r = testapp.get('/{}'.format(job.id))
        assert 'mit:Foobar' in r.text

    def test_job_uses_unknown_for_item_with_no_layer_id(self, testapp, db):
        job = Job(item=Item(uri='674a0ab1-325f-561a-a837-09e9a9a79b91'))
        db.session.add(job)
        db.session.commit()
        r = testapp.get('/{}'.format(job.id))
        assert 'Unknown' in r.text


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
