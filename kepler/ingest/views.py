# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask.views import View
from flask import request, jsonify
from kepler.jobs import create_job
from kepler.models import Job

class IngestView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            return self.show(*args, **kwargs)
        elif request.method == 'POST':
            return self.create()

    def show(self, job_name):
        job = Job.query.filter_by(name=job_name).first_or_404()
        return jsonify(job.as_dict)

    def create(self):
        shapefile = request.files['shapefile']
        metadata = request.files['metadata']
        job = create_job(data=shapefile, metadata=metadata)
        try:
            job.run()
        except Exception:
            job.fail()
            raise
        else:
            job.complete()
            return '', 202

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = cls.as_view(endpoint)
        app.add_url_rule(url, 'index', view_func=view_func, methods=['POST'])
        app.add_url_rule('%s<path:job_name>' % url, 'resource', methods=['GET'],
                         view_func=view_func)
