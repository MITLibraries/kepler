# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.views import View
from flask import request, render_template
from sqlalchemy.sql import func
from sqlalchemy import and_

from kepler.models import Job
from kepler.extensions import db


class JobView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if request.endpoint.endswith('.index'):
                return self.list()
            return self.show(*args, **kwargs)

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
        return render_template('job/index.html', pending=pending,
                               completed=completed, failed=failed)

    def show(self, id):
        job = Job.query.get_or_404(id)
        return render_template('job/show.html', job=job)

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = cls.as_view(endpoint)
        app.add_url_rule(url, 'index', methods=['GET'], view_func=view_func)
        app.add_url_rule('%s<path:id>' % url, 'resource', methods=['GET'],
                         view_func=view_func)
