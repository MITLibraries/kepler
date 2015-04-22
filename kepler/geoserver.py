# -*- coding: utf-8 -*-
from __future__ import absolute_import

import requests
from flask import current_app


def service_url(root_url, workspace):
    base = root_url.rstrip('/') + '/'
    return '%srest/workspaces/%s/' % (base, workspace)


def put_url(id, mimetype):
    svc_url = service_url(current_app.config['GEOSERVER_URL'],
                          current_app.config['GEOSERVER_WORKSPACE'])
    if mimetype == 'application/zip':
        datastore = current_app.config['GEOSERVER_DATASTORE']
        return '%sdatastores/%s/file.shp' % (svc_url, datastore)
    elif mimetype == 'image/tiff':
        return '%scoveragestores/%s/file.geotiff' % (svc_url, id)


def delete_url(id, mimetype):
    svc_url = service_url(current_app.config['GEOSERVER_URL'],
                          current_app.config['GEOSERVER_WORKSPACE'])
    if mimetype == 'application/zip':
        datastore = current_app.config['GEOSERVER_DATASTORE']
        return '%sdatastores/%s/featuretypes/%s?recurse=true' % (svc_url,
                                                                 datastore, id)
    elif mimetype == 'image/tiff':
        return '%scoveragestores/%s?recurse=true' % (svc_url, id)


def put(id, data, mimetype):
    url = put_url(id, mimetype)
    headers = {'Content-type': mimetype}
    r = requests.put(url, data=data, headers=headers)
    r.raise_for_status()


def delete(id, mimetype):
    url = delete_url(id, mimetype)
    r = requests.delete(url)
    r.raise_for_status()
