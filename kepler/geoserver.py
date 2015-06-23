# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io

import requests
from flask import current_app


def wms_url(access):
    return '%swms' % _url_by_access(access)


def wfs_url(access):
    return '%swfs' % _url_by_access(access)


def service_url(root_url, workspace):
    base = root_url.rstrip('/') + '/'
    return '%srest/workspaces/%s/' % (base, workspace)


def put_url(root, id, mimetype):
    svc_url = service_url(root, current_app.config['GEOSERVER_WORKSPACE'])
    if mimetype == 'application/zip':
        datastore = current_app.config['GEOSERVER_DATASTORE']
        return '%sdatastores/%s/file.shp' % (svc_url, datastore)
    elif mimetype == 'image/tiff':
        return '%scoveragestores/%s/file.geotiff' % (svc_url, id)


def delete_url(root, id, mimetype):
    svc_url = service_url(root, current_app.config['GEOSERVER_WORKSPACE'])
    if mimetype == 'application/zip':
        datastore = current_app.config['GEOSERVER_DATASTORE']
        return '%sdatastores/%s/featuretypes/%s?recurse=true' % (svc_url,
                                                                 datastore, id)
    elif mimetype == 'image/tiff':
        return '%scoveragestores/%s?recurse=true' % (svc_url, id)


def put(root, id, data, mimetype):
    url = put_url(root, id, mimetype)
    headers = {'Content-type': mimetype}
    with io.open(data, 'rb') as fp:
        r = requests.put(url, data=fp, headers=headers)
    r.raise_for_status()


def delete(root, id, mimetype):
    url = delete_url(root, id, mimetype)
    r = requests.delete(url)
    r.raise_for_status()


def _url_by_access(access):
    if access.lower() == 'restricted':
        return current_app.config['GEOSERVER_RESTRICTED_URL']
    return current_app.config['GEOSERVER_PUBLIC_URL']
