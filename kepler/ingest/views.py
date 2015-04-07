# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.views import View
from flask import request, jsonify, render_template
from sqlalchemy.sql import func
from sqlalchemy import and_

from kepler.jobs import create_job
from kepler.models import Job
from kepler.extensions import db


class IngestView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if request.endpoint.endswith('.index'):
                return self.index()
            return self.show(*args, **kwargs)
        elif request.method == 'PUT':
            return self.create(*args, **kwargs)

    def index(self):
        pending = []
        completed = []
        failed = []
        sub_q = db.session.query(Job.name, func.max(Job.time).label('time')).\
            group_by(Job.name).subquery()
        q = db.session.query(Job).join(sub_q,
            and_(Job.name==sub_q.c.name, Job.time==sub_q.c.time)).\
            order_by(Job.time.desc())
        for job in q.filter(Job.status=='PENDING'):
            pending.append(job)
        for job in q.filter(Job.status=='COMPLETED'):
            completed.append(job)
        for job in q.filter(Job.status=='FAILED'):
            failed.append(job)
        return render_template('index.html', pending=pending,
                               completed=completed, failed=failed)

    def show(self, job_name):
        job = Job.query.filter_by(name=job_name).order_by(Job.time.desc()).\
            first_or_404()
        return jsonify(job.as_dict)

    def create(self, job_name):
        shapefile = request.files['shapefile']
        metadata = request.files['metadata']
        job = create_job(name=job_name, data=shapefile, metadata=metadata)
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
        app.add_url_rule(url, 'index', methods=['GET'], view_func=view_func)
        app.add_url_rule('%s<path:job_name>' % url, 'resource',
                         methods=['GET', 'PUT'], view_func=view_func)
