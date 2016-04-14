# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io


class GeoService(object):
    def __init__(self, session, url, workspace, datastore):
        self.session = session
        self.url = url
        self.workspace = workspace
        self.datastore = datastore

    @property
    def service_url(self):
        url = self.url.rstrip('/') + '/'
        return '%srest/workspaces/%s/' % (url, self.workspace)

    @property
    def wms_url(self):
        return '%s/wms' % self.url.rstrip('/')

    @property
    def wfs_url(self):
        return '%s/wfs' % self.url.rstrip('/')

    def put(self, id, data, mimetype):
        url = self._put_url(id, mimetype)
        headers = {'Content-type': mimetype}
        with io.open(data, 'rb') as fp:
            r = self.session.put(url, data=fp, headers=headers)
        r.raise_for_status()
        return self.layer_id(url.rsplit('/', 1)[0], mimetype)

    def layer_id(self, url, mimetype):
        if mimetype == 'application/zip':
            name = self.feature_type_name(self.feature_types(url))
        elif mimetype == 'image/tiff':
            name = self.coverage_name(self.coverages(url))
        return '%s:%s' % (self.workspace, name)

    def feature_types(self, url):
        json = self._get_json(url)
        return json['dataStore']['featureTypes']

    def feature_type_name(self, url):
        json = self._get_json(url)
        return json['featureTypes']['featureType'][0]['name']

    def coverages(self, url):
        json = self._get_json(url)
        return json['coverageStore']['coverages']

    def coverage_name(self, url):
        json = self._get_json(url)
        return json['coverages']['coverage'][0]['name']

    def _get_json(self, url):
        r = self.session.get(url, headers={'Accept': 'application/json'})
        print(r.content)
        r.raise_for_status()
        return r.json()

    def _put_url(self, id, mimetype):
        if mimetype == 'application/zip':
            return '%sdatastores/%s/file.shp' % (self.service_url,
                                                 self.datastore)
        elif mimetype == 'image/tiff':
            return '%scoveragestores/%s/file.geotiff' % (self.service_url,
                                                         id)
