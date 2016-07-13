# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io


class GeoService(object):
    def __init__(self, session, url, workspace, datastore):
        self.session = session
        self.url = url
        self.workspace = workspace
        self.datastore = datastore
        self.shapefile_import = {
            'import': {
                'targetStore': {
                    'dataStore': {
                        'name': self.datastore
                    }
                },
                'targetWorkspace': {
                    'workspace': {
                        'name': self.workspace
                    }
                }
            }
        }
        self.geotiff_import = {
            'import': {
                'targetWorkspace': {
                    'workspace': {
                        'name': self.workspace
                    }
                }
            }
        }

    @property
    def service_url(self):
        url = self.url.rstrip('/')
        return '{}/rest/imports/'.format(url)

    @property
    def wms_url(self):
        return '%s/wms' % self.url.rstrip('/')

    @property
    def wfs_url(self):
        return '%s/wfs' % self.url.rstrip('/')

    def put(self, data, ftype, name):
        if ftype == 'shapefile':
            import_url = self._create_import(self.shapefile_import)
        elif ftype == 'geotiff':
            import_url = self._create_import(self.geotiff_import)
        else:
            raise Exception('unknown format')
        task_url = self._create_upload_task(
            '{}/tasks'.format(import_url.rstrip('/')), data)
        self._set_task_method(task_url, name, ftype)
        self._run_import(import_url)
        return import_url

    def _create_import(self, data):
        r = self.session.post(self.service_url, json=data)
        r.raise_for_status()
        return r.headers.get('location')

    def _run_import(self, url):
        r = self.session.post('{}?async=true'.format(url))
        r.raise_for_status()

    def _create_upload_task(self, url, data):
        with io.open(data, 'rb') as fp:
            r = self.session.post(url, files={'filedata': fp})
        r.raise_for_status()
        return r.headers.get('location')

    def _set_task_method(self, url, name, ftype):
        shape = '{}/rest/workspaces/{}/datastores/{}/featuretypes/{}'
        tiff = '{}/rest/workspaces/{}/coveragestores/{}/coverages/{}'
        if ftype == 'shapefile':
            r = self.session.get(shape.format(self.url.rstrip('/'),
                                              self.workspace, self.datastore,
                                              name))
        elif ftype == 'geotiff':
            r = self.session.get(tiff.format(self.url.rstrip('/'),
                                             self.workspace, name, name))
        if r.status_code == 200:
            self.session.put(url, json={'task': {'updateMode': 'REPLACE'}})
