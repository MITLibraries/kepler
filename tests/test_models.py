# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

from kepler.extensions import db
from kepler.models import Job
from tests import BaseTestCase


class JobTestCase(BaseTestCase):
    def testJobHasRepresentation(self):
        job = Job(name=u'♄')
        db.session.add(job)
        db.session.commit()
        self.assertEqual(repr(job), '<Job #%d: %r>' % (job.id, job.name))

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
        job = Job(name=u'♄')
        db.session.add(job)
        db.session.commit()
        self.assertEqual(job.as_dict['id'], job.id)

    def testJobHasTime(self):
        time = datetime.now()
        job = Job(time=time)
        db.session.add(job)
        db.session.commit()
        self.assertEqual(job.time, time)
