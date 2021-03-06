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
    status = db.Column(db.Enum(u'CREATED', u'PENDING', u'COMPLETED', u'FAILED',
                               name='status'), default=u'CREATED')
    import_url = db.Column(db.String())
    time = db.Column(db.DateTime(timezone=True), default=datetime.now)
    error_msg = db.Column(db.Text())
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
    access = db.Column(db.Enum(u'Public', u'Restricted', name='access'),
                       default=u'Public')
    jobs = db.relationship('Job', backref='item', lazy='dynamic')
    tiff_url = db.Column(db.Unicode(255))
    record = db.Column(db.Text())

    def __repr__(self):
        return '<Item #%d: %r>' % (self.id, self.uri)

    def as_dict(self):
        return {
            'uri': self.uri,
            'status': self.jobs.order_by(Job.time.desc()).first().status
        }
