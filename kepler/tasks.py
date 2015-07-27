# -*- coding: utf-8 -*-
"""
    kepler.tasks
    ------------

    This module provides a set of tasks that send data to different Web
    services. Each task has the same signature::

        task(job, data)

    In most cases, the data will be an absolute path to a
    `bag <https://tools.ietf.org/html/draft-kunze-bagit-10>`_.
"""

from __future__ import absolute_import
import io
import json
import tempfile
import uuid

from flask import current_app
from ogre.xml import FGDCParser

from kepler.geoserver import put, wfs_url, wms_url
from kepler.bag import get_fgdc, get_shapefile, get_geotiff
from kepler.records import create_record, MitRecord
from kepler.services.solr import SolrServiceManager
from kepler.git import repository
from kepler import sword
from kepler.utils import make_uuid
from kepler.extensions import db
from kepler.parsers import MarcParser


def index_shapefile(job, data):
    """Index an uploaded Shapefile in Solr.

        :param job: :class:`~kepler.models.Job`
        :param bag: absolute path to bag containing Shapefile
    """

    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms': wms_url(job.item.access),
        'http://www.opengis.net/def/serviceType/ogc/wfs': wfs_url(job.item.access),
    }
    _index_from_fgdc(job, bag=data, dct_references_s=refs)


def index_geotiff(job, data):
    """Index an uploaded GeoTIFF file in Solr.

    :param job: :class:`~kepler.models.Job`
    :param bag: absolute path to bag containing GeoTIFF
    """

    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms': wms_url(job.item.access),
        'http://schema.org/downloadUrl': job.item.handle
    }
    _index_from_fgdc(job, bag=data, dct_references_s=refs)


def index_repo_records(job, repo):
    _index_records(_load_repo_records(repo))


def submit_to_dspace(job, data):
    username = current_app.config['SWORD_SERVICE_USERNAME']
    password = current_app.config['SWORD_SERVICE_PASSWORD']
    pkg = sword.SWORDPackage(uuid=job.item.uri)
    tiff = get_geotiff(data)
    pkg.datafiles.append(tiff)
    with tempfile.NamedTemporaryFile(suffix='.zip') as fp:
        pkg.write(fp)
        handle = sword.submit(current_app.config['SWORD_SERVICE_URL'], fp.name,
                              auth=(username, password))
    job.item.handle = handle
    db.session.commit()


def upload_shapefile(job, data):
    """Upload Shapefile to GeoServer.

        :param job: :class:`~kepler.models.Job`
        :param bag: absolute path to bag containing Shapefile
    """

    _upload_to_geoserver(job, bag=data, mimetype='application/zip')


def upload_geotiff(job, data):
    """Upload GeoTIFF to GeoServer.

        :param job: :class:`~kepler.models.Job`
        :param bag: absolute path to bag containing GeoTIFF
    """

    _upload_to_geoserver(job, bag=data, mimetype='image/tiff')


def index_marc_records(job, data):
    _index_records(_load_marc_records(data))


def _index_from_fgdc(job, bag, **kwargs):
    """Index a GeoServer-bound layer from the attached FGDC metadata.

    This will pull the FGDC metadata out of the Bag and add any necessary
    fields before indexing in Solr.

    :param job: :class:`~kepler.models.Job`
    :param bag: absolute path to bag containing FGDC metadata
    :param \**kwargs: additional fields to add to the record
    """

    uid = uuid.UUID(job.item.uri)
    layer_id = "%s:%s" % (current_app.config['GEOSERVER_WORKSPACE'], uid)
    kwargs.update({
        "layer_id_s": layer_id,
        "uuid": str(uid),
    })
    fgdc = get_fgdc(bag)
    record = create_record(fgdc, FGDCParser, **kwargs)
    _index_records([record.as_dict()])


def _upload_to_geoserver(job, bag, mimetype):
    """Uploads Shapefiles and GeoTIFFs to GeoServer.

    This is a generic task for uploading data to GeoServer. You should
    instead use the specific data type functions: :func:`~upload_shapefile`
    and :func:`~upload_geotiff`.

    :param job: :class:`~kepler.models.Job`
    :param bag: absolute path to bag containing Shapefile or GeoTIFF
    :param mimetype: one of ``application/zip`` or ``image/tiff``
    """

    if mimetype == 'application/zip':
        data = get_shapefile(bag)
    elif mimetype == 'image/tiff':
        data = get_geotiff(bag)
    if job.item.access == 'Restricted':
        url = current_app.config['GEOSERVER_RESTRICTED_URL']
    else:
        url = current_app.config['GEOSERVER_PUBLIC_URL']
    layer_id = put(url, job.item.uri, data, mimetype)
    job.item.layer_id = layer_id
    db.session.commit()


def _index_records(records):
    """Indexes records in Solr.

    :param records: iterator of dictionaries to be added to Solr
    """

    solr = SolrServiceManager(current_app.config['SOLR_URL'])
    solr.postMetaDataToServer(records)


def _load_repo_records(repo):
    for item in repository(repo):
        with io.open(item.solr_json, encoding='utf-8') as fp:
            yield json.load(fp)


def _load_marc_records(data):
    for record in MarcParser(data):
        uid = make_uuid(record['_marc_id'],
                        current_app.config['UUID_NAMESPACE'])
        record.update(uuid=uid)
        yield MitRecord(**record).as_dict()
