# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import partial
import io
import json

from flask import current_app
from ogre.xml import FGDCParser

from kepler import compose
from kepler.geoserver import put
from kepler.bag import read_fgdc
from kepler.records import create_record
from kepler.services.solr import SolrServiceManager
from kepler.git import repository


def tasks(task_list):
    return compose(*reversed(task_list))


def upload_to_geoserver(record, data, mimetype):
    put(record._filename, data, mimetype)
    return record, data


def index_record(record, data=None):
    solr = SolrServiceManager(current_app.config['SOLR_URL'])
    solr.postMetaDataToServer([record.as_dict()])
    return record, data


def make_record(job, data, **kwargs):
    layer_id = "%s:%s" % (current_app.config['GEOSERVER_WORKSPACE'],
                          job.item.uri)
    properties = {
        'layer_id_s': layer_id,
        '_filename': job.item.uri,
    }
    properties.update(kwargs)
    fgdc = read_fgdc(data)
    return create_record(fgdc, FGDCParser, **properties), data


def index_records(records):
    solr = SolrServiceManager(current_app.config['SOLR_URL'])
    solr.postMetaDataToServer(records)


def load_repo_records(repo):
    for item in repository(repo):
        with io.open(item.solr_json, encoding='utf-8') as fp:
            yield json.load(fp)


shapefile_upload_task = partial(upload_to_geoserver, mimetype='application/zip')
tiff_upload_task = partial(upload_to_geoserver, mimetype='image/tiff')
