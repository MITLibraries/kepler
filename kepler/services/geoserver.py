# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests
from flask import current_app


class GeoServerResource(object):
    def put(self, data):
        headers = {'Content-type': self.mimetype}
        r = requests.put(self._put, data=data, headers=headers)
        r.raise_for_status()

    def delete(self):
        r = requests.delete(self._delete)
        r.raise_for_status()


class ShapefileResource(GeoServerResource):
    mimetype = 'application/zip'

    def __init__(self, id):
        base = current_app.config['GEOSERVER_URL'].rstrip('/') + '/'
        workspace = current_app.config['GEOSERVER_WORKSPACE']
        service = '%srest/workspaces/%s/' % (base, workspace)
        datastore = current_app.config['GEOSERVER_DATASTORE']
        self._read = '%sdatastores/%s/featuretypes/%s' % (service, datastore,
                                                         id)
        self._delete = '%sdatastores/%s/featuretypes/%s?recurse=true' % (
            service, datastore, id)
        self._put = '%sdatastores/%s/file.shp' % (service, datastore)


class GeoTiffResource(GeoServerResource):
    mimetype = 'image/tiff'

    def __init__(self, id):
        base = current_app.config['GEOSERVER_URL'].rstrip('/') + '/'
        workspace = current_app.config['GEOSERVER_WORKSPACE']
        service = '%srest/workspaces/%s/' % (base, workspace)
        self._read = '%scoveragestores/%s/coverages/%s' % (service, id, id)
        self._delete = '%scoveragestores/%s?recurse=true' % (service, id)
        self._put = '%scoveragestores/%s/file.geotiff' % (service, id)
