# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from kepler.extensions import db


def get_or_create(Model, **kwargs):
    instance = Model.query.filter_by(**kwargs).first()
    if not instance:
        instance = Model(**kwargs)
        db.session.add(instance)
    return instance


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(u'PENDING', u'COMPLETED', u'FAILED'),
                       default=u'PENDING')
    time = db.Column(db.DateTime(timezone=True), default=datetime.now)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __repr__(self):
        return '<Job #%d>' % (self.id,)

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'item': self.item.uri,
            'status': self.status
        }


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Unicode(255), unique=True)
    layer_id = db.Column(db.Unicode(255))
    handle = db.Column(db.Unicode(255))
    access = db.Column(db.Enum(u'Public', u'Restricted'), default=u'Public')
    jobs = db.relationship('Job', backref='item', lazy='dynamic')
    tiff_url = db.Column(db.Unicode(255))

    def __repr__(self):
        return '<Item #%d: %r>' % (self.id, self.uri)
