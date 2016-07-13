# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path

from flask import request, jsonify
from flask.views import View

from kepler import client_auth_required
from kepler.extensions import req
from kepler.jobs import create_job, run_job
from kepler.models import Item
from kepler.utils import request_wants_json


class LayerView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'PUT':
            return self.create(*args, **kwargs)
        else:
            return self.show(*args, **kwargs)

    def show(self, id):
        uuid, ext = os.path.splitext(id)
        item = Item.query.filter(Item.uri == uuid).first_or_404()
        if request_wants_json() or ext == '.json':
            return jsonify(item.as_dict())
        else:
            return ''

    def create(self, id):
        job = create_job(id)
        req.q.enqueue(run_job, job.id)
        return '', 201

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = client_auth_required(cls.as_view(endpoint))
        app.add_url_rule('{}<id>'.format(url), 'resource',
                         methods=['GET', 'PUT'], view_func=view_func)
