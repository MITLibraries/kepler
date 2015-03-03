# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app
from requests.exceptions import HTTPError
from kepler.models import Job
from kepler.extensions import db
from kepler.exceptions import UnsupportedFormat
from kepler.services.geoserver import GeoServerServiceManager
from kepler.services.solr import SolrServiceManager
from kepler.parsers import FgdcParser
from kepler.records import create_record

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
        workspace = current_app.config['GEOSERVER_WORKSPACE']
        datastore = current_app.config['GEOSERVER_DATASTORE']
        layer_id = "%s:%s" % (current_app.config['GEOSERVER_WORKSPACE'],
                              self.job.name)
        properties = {
            'dct_provenance_s': 'MIT',
            'dc_type_s': 'Dataset',
            'layer_id_s': layer_id,
            '_filename': self.job.name,
        }
        record = create_record(self.metadata, FgdcParser, **properties)
        mgr = GeoServerServiceManager(url, workspace, datastore)
        mgr.upload(self.data, self.data.mimetype)
        try:
            solr = SolrServiceManager(current_app.config['SOLR_URL'])
            solr.postMetaDataToServer([record.as_dict()])
        except (AttributeError, HTTPError):
            mgr.delete(self.data.filename)
            raise


class GeoTiffUploadJob(UploadJob):
    pass
