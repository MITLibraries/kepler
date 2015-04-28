# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.views import View
from flask import request, jsonify, render_template
from sqlalchemy.sql import func
from sqlalchemy import and_

from kepler.jobs import create_job
from kepler.models import Job, Item
from kepler.extensions import db


class JobView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if request.endpoint.endswith('.index'):
                return self.list()
            return self.show(*args, **kwargs)
        if request.method == 'POST':
            return self.create(*args, **kwargs)

    def list(self):
        pending = []
        completed = []
        failed = []
        sub_q = db.session.query(Job.item_id, func.max(Job.time).label('time')).\
            group_by(Job.item_id).subquery()
        q = db.session.query(Job).\
            join(sub_q, and_(Job.item_id == sub_q.c.item_id,
                             Job.time == sub_q.c.time)).\
            order_by(Job.time.desc())
        for job in q.filter(Job.status == 'PENDING'):
            pending.append(job)
        for job in q.filter(Job.status == 'COMPLETED'):
            completed.append(job)
        for job in q.filter(Job.status == 'FAILED'):
            failed.append(job)
        return render_template('index.html', pending=pending,
                               completed=completed, failed=failed)

    def show(self, job_name):
        job = Job.query.join(Item).filter(Item.uri == job_name).\
            order_by(Job.time.desc()).first_or_404()
        return jsonify(job.as_dict)

    def create(self):
        job = create_job(request.form['type'], request.form['uuid'],
                         request.files.get('file'))
        job()
        return '', 201

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = cls.as_view(endpoint)
        app.add_url_rule(url, 'index', methods=['GET'], view_func=view_func)
        app.add_url_rule(url, 'resource', methods=['POST'], view_func=view_func)
        app.add_url_rule('%s<path:job_name>' % url, 'resource',
                         methods=['GET'], view_func=view_func)
