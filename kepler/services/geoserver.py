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
        self.url = urljoin(url,
            "rest/workspaces/%s/datastores/%s/file.shp" % (workspace, datastore))

    def upload(self, fstream, mimetype):
        headers = {'Content-type': mimetype}
        r = requests.put(self.url, data=fstream, headers=headers)
        r.raise_for_status()
