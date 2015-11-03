# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path
import shutil
import tempfile
import uuid

from flask import request
from flask.views import View

from kepler import client_auth_required
from kepler.bag import unpack, get_datatype, get_access
from kepler.exceptions import UnsupportedFormat
from kepler.jobs import create_job
from kepler.tasks import (upload_shapefile, index_shapefile, upload_geotiff,
                          index_geotiff, submit_to_dspace,)


class LayerView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'POST':
            return self.create(*args, **kwargs)

    def create(self, *args, **kwargs):
        data = request.files['file']
        uid = os.path.splitext(os.path.basename(data.filename))[0]
        uri = uuid.UUID(uid).urn
        tmpdir = tempfile.mkdtemp()
        try:
            bag = unpack(data, tmpdir)
            datatype = get_datatype(bag)
            if datatype == 'shapefile':
                tasks = [upload_shapefile, index_shapefile, ]
            elif datatype == 'geotiff':
                tasks = [upload_geotiff, submit_to_dspace, index_geotiff, ]
            else:
                raise UnsupportedFormat(datatype)
            access = get_access(bag)
            job = create_job(uri, bag, tasks, access)
            job()
        finally:
            shutil.rmtree(tmpdir)
        return '', 201

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = client_auth_required(cls.as_view(endpoint))
        app.add_url_rule(url, 'resource', methods=['POST'], view_func=view_func)
