# -*- coding: utf-8 -*-
from __future__ import absolute_import
from kepler.models import Job
from kepler.extensions import db
from kepler.exceptions import UnsupportedFormat

def create_job(data, metadata=None):
    name = data.filename.decode('utf-8')
    job = Job(name=name, status=u'PENDING')
    db.session.add(job)
    db.session.commit()
    try:
        if data.mimetype == 'application/zip':
            instance = ShapefileUploadJob(job, data=data, metadata=metadata)
        elif data.mimetype == 'image/tiff':
            instance = GeoTiffUploadJob(job, data=data, metadata=metadata)
        else:
            raise UnsupportedFormat(data.mimetype)
    except Exception:
        job.status = u'FAILED'
        db.session.commit()
        raise
    return instance


class UploadJob(object):
    def __init__(self, job, data, metadata=None):
        self.job = job
        self.data = data
        self.metadata = metadata

    def fail(self):
        self.job.status = u'FAILED'
        db.session.commit()

    def complete(self):
        self.job.status = u'COMPLETED'
        db.session.commit()

    def run(self):
        raise NotImplementedError


class ShapefileUploadJob(UploadJob):
    def run(self):
        pass


class GeoTiffUploadJob(UploadJob):
    pass
