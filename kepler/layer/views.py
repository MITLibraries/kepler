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
from kepler.extensions import req
from kepler.jobs import create_job, run_job
from kepler.tasks import (upload_shapefile, index_shapefile, upload_geotiff,
                          index_geotiff, submit_to_dspace,)


class LayerView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'PUT':
            return self.create(*args, **kwargs)

    def create(self, id):
        job = create_job(id)
        req.q.enqueue(run_job, job.id)
        return '', 201

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = client_auth_required(cls.as_view(endpoint))
        app.add_url_rule('{}<path:id>'.format(url), 'resource', methods=['PUT'],
                         view_func=view_func)
