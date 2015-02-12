# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app
from kepler.models import Job
from kepler.extensions import db
from kepler.exceptions import UnsupportedFormat
from kepler.services.geoserver import GeoServerServiceManager
from kepler.parsers import FgdcParser

def create_job(data, metadata=None):
    name = data.filename
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
        url = current_app.config['GEOSERVER_URL']
        mgr = GeoServerServiceManager(url)
        mgr.upload(self.data)

    def create_record(self, metadata):
        records = FgdcParser(metadata)
        return next(iter(records))


class GeoTiffUploadJob(UploadJob):
    pass
