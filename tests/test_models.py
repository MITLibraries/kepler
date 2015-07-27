# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

import pytest
from sqlalchemy.exc import SQLAlchemyError

from kepler.models import Job, Item, get_or_create


class TestGetOrCreate(object):
    def testReturnsExistingItem(self, db):
        item = Item(uri=u'foobar')
        db.session.add(item)
        db.session.commit()
        assert get_or_create(Item, uri=u'foobar') == item

    def testCreatesItemIfNotExists(self, db):
        item = get_or_create(Item, uri=u'foobaz')
        assert item.uri == u'foobaz'


class TestJob(object):
    def testJobHasRepresentation(self, db):
        job = Job()
        db.session.add(job)
        db.session.commit()
        assert repr(job) == '<Job #%d>' % (job.id,)

    def testJobHasStatus(self, db):
        job = Job(status=u'PENDING')
        db.session.add(job)
        db.session.commit()
        assert job.status == u'PENDING'

    def testJobHasDefaultStatusPending(self, db):
        job = Job()
        db.session.add(job)
        db.session.commit()
        assert job.status == u'PENDING'

    def testJobCanBeSerializedAsDictionary(self, db):
        job = Job(item=Item(uri=u'♄'))
        db.session.add(job)
        db.session.commit()
        assert job.as_dict['id'] == job.id

    def testJobHasTime(self, db):
        time = datetime.now()
        job = Job(time=time)
        db.session.add(job)
        db.session.commit()
        assert job.time == time


class TestItem(object):
    def testItemHasRepresentation(self, db):
        item = Item(uri=u'fleventy-five')
        db.session.add(item)
        db.session.commit()
        assert repr(item) == '<Item #%d: %r>' % (item.id, item.uri)

    def testUriIsUnique(self, db):
        item_one = Item(uri=u'fleventy-five')
        item_two = Item(uri=u'fleventy-five')
        db.session.add_all([item_one, item_two])
        with pytest.raises(SQLAlchemyError):
            db.session.commit()

    def testItemHasAccessLevel(self, db):
        item = Item(access=u'Public')
        assert item.access == u'Public'

    def testItemAccessDefaultsToPublic(self, db):
        item = Item()
        db.session.add(item)
        db.session.commit()
        assert item.access == u'Public'

    def testItemHasLayerId(self, db):
        item = Item(layer_id='foo:bar')
        assert item.layer_id == 'foo:bar'
