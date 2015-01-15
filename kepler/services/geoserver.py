# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests

class GeoServerServiceManager(object):
    def __init__(self, url):
        self.url = url

    def upload(self, fstream):
        r = requests.put(self.url, fstream)
        r.raise_for_status()
