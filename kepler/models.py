# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from kepler.extensions import db


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    status = db.Column(db.Enum(u'PENDING', u'COMPLETED', u'FAILED'),
                       default=u'PENDING')
    time = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __repr__(self):
        return '<Job #%d: %r>' % (self.id, self.name)

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }
