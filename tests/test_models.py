# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from kepler.extensions import db
from kepler.models import Job, Item, get_or_create
from tests import BaseTestCase


class GetOrCreateTestCase(BaseTestCase):
    def testReturnsExistingItem(self):
        item = Item(uri=u'foobar')
        db.session.add(item)
        db.session.commit()
        self.assertEqual(get_or_create(Item, uri=u'foobar'), item)

    def testCreatesItemIfNotExists(self):
        item = get_or_create(Item, uri=u'foobaz')
        self.assertEqual(item.uri, u'foobaz')


class JobTestCase(BaseTestCase):
    def testJobHasRepresentation(self):
        job = Job()
        db.session.add(job)
        db.session.commit()
        self.assertEqual(repr(job), '<Job #%d>' % (job.id,))

    def testJobHasStatus(self):
        job = Job(status=u'PENDING')
        db.session.add(job)
        db.session.commit()
        self.assertEqual(job.status, 'PENDING')

    def testJobHasDefaultStatusPending(self):
        job = Job()
        db.session.add(job)
        db.session.commit()
        self.assertEqual(job.status, 'PENDING')

    def testJobCanBeSerializedAsDictionary(self):
        job = Job(item=Item(uri=u'♄'))
        db.session.add(job)
        db.session.commit()
        self.assertEqual(job.as_dict['id'], job.id)

    def testJobHasTime(self):
        time = datetime.now()
        job = Job(time=time)
        db.session.add(job)
        db.session.commit()
        self.assertEqual(job.time, time)


class ItemTestCase(BaseTestCase):
    def testItemHasRepresentation(self):
        item = Item(uri=u'fleventy-five')
        db.session.add(item)
        db.session.commit()
        self.assertEqual(repr(item), '<Item #%d: %r>' % (item.id, item.uri))

    def testUriIsUnique(self):
        item_one = Item(uri=u'fleventy-five')
        item_two = Item(uri=u'fleventy-five')
        db.session.add_all([item_one, item_two])
        with self.assertRaises(SQLAlchemyError):
            db.session.commit()
