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
import tempfile
import uuid

from flask import current_app
from ogre.xml import FGDCParser
from lxml import etree
import pysolr
import requests
from sqlalchemy import and_
from sqlalchemy.sql import func

from kepler import sword
from kepler.bag import (get_fgdc, get_shapefile, get_geotiff, get_access,
                        get_shapefile_name, get_geotiff_name)
from kepler.models import Job
from kepler.records import create_record, MitRecord
from kepler.utils import make_uuid
from kepler.extensions import db, solr as solr_session, geoserver, dspace
from kepler.parsers import MarcParser
from kepler.geo import compress, pyramid

try:
    from itertools import imap as map
except ImportError:
    pass


def index_shapefile(job, data):
    """Index an uploaded Shapefile in Solr.

        :param job: :class:`~kepler.models.Job`
        :param bag: absolute path to bag containing Shapefile
    """

    access = get_access(data)
    gs = _get_geoserver(access)
    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms': gs.wms_url,
        'http://www.opengis.net/def/serviceType/ogc/wfs': gs.wfs_url,
    }
    uid = uuid.UUID(job.item.uri)
    shp_name = get_shapefile_name(data)
    layer_id = "%s:%s" % (gs.workspace, shp_name)
    job.item.layer_id = layer_id
    db.session.commit()
    _index_from_fgdc(job, bag=data, dct_references_s=refs, uuid=str(uid),
                     layer_id_s=layer_id)


def index_geotiff(job, data):
    """Index an uploaded GeoTIFF file in Solr.

    :param job: :class:`~kepler.models.Job`
    :param bag: absolute path to bag containing GeoTIFF
    """

    access = get_access(data)
    gs = _get_geoserver(access)
    refs = {
        'http://www.opengis.net/def/serviceType/ogc/wms': gs.wms_url,
        'http://schema.org/downloadUrl': job.item.tiff_url
    }
    uid = uuid.UUID(job.item.uri)
    layer_id = "%s:%s" % (gs.workspace, uid)
    job.item.layer_id = layer_id
    db.session.commit()
    _index_from_fgdc(job, bag=data, dct_references_s=refs, uuid=str(uid),
                     layer_id_s=layer_id)


def submit_to_dspace(job, data):
    """Upload GeoTIFF to DSpace.

        .. note:: only runs if `Item.handle` has not previously been set.

        :param job: :class:`~kepler.models.Job`
        :param data: absolute path to bag containing GeoTIFF
    """
    if not job.item.handle:
        pkg = sword.SWORDPackage(uuid=job.item.uri)
        tiff = get_geotiff(data)
        pkg.datafiles.append(tiff)
        pkg.metadata = _fgdc_to_mods(get_fgdc(data))
        with tempfile.NamedTemporaryFile(suffix='.zip') as fp:
            pkg.write(fp)
            handle = sword.submit(current_app.config['SWORD_SERVICE_URL'],
                                  fp.name)
        job.item.handle = handle
        db.session.commit()


def get_geotiff_url_from_dspace(job):
    """Retrieve the GeoTIFF URL from a DSpace Handle.

        .. note:: assumes the OAI-ORE only contains a single TIFF.

        :param job: :class:`~kepler.models.Job`
    """
    handle = job.item.handle.replace('http://hdl.handle.net/', '')
    ore_url = current_app.config['OAI_ORE_URL'] + handle + '/ore.xml'
    r = dspace.session.get(ore_url)
    r.raise_for_status()
    doc = etree.fromstring(r.content)
    tif_urls = doc.xpath(
        '//rdf:Description/@rdf:about[contains(., ".tif")]',
        namespaces={'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})

    if len(tif_urls) != 1:
        raise Exception('Expected 1 tiff, found ' + str(len(tif_urls)))
    else:
        job.item.tiff_url = tif_urls[0]

    db.session.commit()


def upload_shapefile(job, data):
    """Upload Shapefile to GeoServer.

        :param job: :class:`~kepler.models.Job`
        :param data: absolute path to bag containing Shapefile
    """

    shp = get_shapefile(data)
    access = get_access(data)
    name = get_shapefile_name(data)
    import_url = _upload_to_geoserver(shp, 'shapefile', access, name)
    job.import_url = import_url
    db.session.commit()


def upload_geotiff(job, data):
    """Upload GeoTIFF to GeoServer.

        :param job: :class:`~kepler.models.Job`
        :param data: absolute path to bag containing GeoTIFF
    """

    tiff = get_geotiff(data)
    access = get_access(data)
    name = get_geotiff_name(data)
    with tempfile.NamedTemporaryFile(suffix='.tif') as fp:
        compress(tiff, fp.name)
        pyramid(fp.name)
        import_url = _upload_to_geoserver(fp.name, 'geotiff', access, name)
    job.import_url = import_url
    db.session.commit()


def resolve_pending_jobs():
    geo_session = requests.Session()
    geo_session.auth = (current_app.config.get('GEOSERVER_AUTH_USER'),
                        current_app.config.get('GEOSERVER_AUTH_PASS'))
    sub_q = db.session.query(Job.item_id, func.max(Job.time).label('time')).\
        group_by(Job.item_id).subquery()
    q = db.session.query(Job).\
        join(sub_q, and_(Job.item_id == sub_q.c.item_id,
                         Job.time == sub_q.c.time)).\
        order_by(Job.time.desc())
    for job in q.filter(Job.status == 'PENDING'):
        r = geo_session.get(job.import_url)
        r.raise_for_status()
        state = r.json()['import']['state']
        if state == 'COMPLETE':
            job.status = 'COMPLETED'
            db.session.commit()


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

    fgdc = get_fgdc(bag)
    record = create_record(fgdc, FGDCParser, **kwargs)
    _index_records([record.as_dict()])


def _upload_to_geoserver(data, filetype, access, name):
    """Uploads Shapefiles and GeoTIFFs to GeoServer.

    This is a generic task for uploading data to GeoServer. You should
    instead use the specific data type functions: :func:`~upload_shapefile`
    and :func:`~upload_geotiff`.

    :param job: :class:`~kepler.models.Job`
    :param data: absolute path to either Shapefile or GeoTIFF
    :param mimetype: one of ``application/zip`` or ``image/tiff``
    """

    gs = _get_geoserver(access)
    import_url = gs.put(data, filetype, name)
    return import_url


def _index_records(records):
    """Indexes records in Solr.

    :param records: iterator of dictionaries to be added to Solr
    """

    solr = pysolr.Solr(current_app.config['SOLR_URL'])
    solr.session = solr_session.session
    solr.add(map(_prep_solr_record, records))


def _load_marc_records(data):
    for record in MarcParser(data):
        uid = make_uuid(record['_marc_id'],
                        current_app.config['UUID_NAMESPACE'])
        record.update(uuid=uid)
        yield MitRecord(**record).as_dict()


def _fgdc_to_mods(fgdc):
    xslt = current_app.config['FGDC_MODS_XSLT']
    xform = etree.XSLT(etree.parse(xslt))
    doc = etree.parse(fgdc)
    mods = xform(doc)
    return etree.tostring(mods, encoding="unicode")


def _prep_solr_record(record):
    """Normalize field values for pysolr.

    `pysolr` does not handle sets, so these need to be converted to
    lists before being added to solr.
    """
    return {k: _normalize_sets(v) for k, v in record.items()}


def _normalize_sets(value):
    if isinstance(value, set):
        return list(value)
    return value


def _get_geoserver(access):
    if access.lower() == 'restricted':
        return geoserver.secure
    return geoserver.public
