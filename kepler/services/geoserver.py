# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class GeoServerServiceManager(object):
    def __init__(self, url, workspace, datastore):
        url = url.rstrip('/') + '/'
        self.base_url = urljoin(url,
            "rest/workspaces/%s/datastores/%s/" % (workspace, datastore))

    def upload(self, fstream, mimetype):
        headers = {'Content-type': mimetype}
        url = "%sfile.shp" % self.base_url
        r = requests.put(url, data=fstream, headers=headers)
        r.raise_for_status()

    def delete(self, filename):
        url = "%sfeaturetypes/%s?recurse=true" % (self.base_url, filename)
        r = requests.delete(url)
        r.raise_for_status()
