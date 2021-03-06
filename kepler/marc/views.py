# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import tempfile
import uuid

from flask import request
from flask.views import View

from kepler import client_auth_required
from kepler.extensions import req
from kepler.jobs import create_job
from kepler.tasks import index_marc_records


class MarcView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'POST':
            return self.create(*args, **kwargs)

    def create(self, *args, **kwargs):
        data = request.files['file']
        uid = uuid.uuid5(uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu'),
                         'marc_records')
        tmpf = tempfile.mkstemp()[1]
        try:
            data.save(tmpf)
            job = create_job(uid.urn, tmpf,
                             [index_marc_records, ], 'Public')
        except:
            os.remove(tmpf)
            raise
        req.q.enqueue(job)
        return '', 201

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = client_auth_required(cls.as_view(endpoint))
        app.add_url_rule(url, 'resource', methods=['POST'],
                         view_func=view_func)
