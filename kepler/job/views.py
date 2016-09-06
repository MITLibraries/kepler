# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.views import View
from flask import request, render_template
from flask_paginate import Pagination
from sqlalchemy.sql import func
from sqlalchemy import and_

from kepler.models import Job
from kepler.extensions import db


class JobView(View):
    PER_PAGE = 15

    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if request.endpoint.endswith('.index'):
                return self.list()
            elif request.endpoint.endswith('.status'):
                return self.filtered(*args, **kwargs)
            return self.show(*args, **kwargs)

    def list(self):
        sub_q = db.session.query(Job.item_id, func.max(Job.time).
                                 label('time')).\
            group_by(Job.item_id).subquery()
        q = db.session.query(Job).\
            join(sub_q, and_(Job.item_id == sub_q.c.item_id,
                             Job.time == sub_q.c.time))
        pending = q.filter(Job.status == 'PENDING').\
            order_by(Job.time.desc()).limit(self.PER_PAGE)
        completed = q.filter(Job.status == 'COMPLETED').\
            order_by(Job.time.desc()).limit(self.PER_PAGE)
        failed = q.filter(Job.status == 'FAILED').\
            order_by(Job.time.desc()).limit(self.PER_PAGE)
        return render_template('job/index.html', pending=pending,
                               completed=completed, failed=failed)

    def filtered(self, status, page=1):
        offset = max(page-1, 0) * self.PER_PAGE
        sub_q = db.session.query(Job.item_id, func.max(Job.time).
                                 label('time')).\
            group_by(Job.item_id).subquery()
        jobs_q = db.session.query(Job).\
            join(sub_q, and_(Job.item_id == sub_q.c.item_id,
                             Job.time == sub_q.c.time,
                             Job.status == status.upper()))
        jobs = jobs_q.\
            order_by(Job.time.desc()).\
            limit(self.PER_PAGE).\
            offset(offset)
        pagination = Pagination(page=page, total=jobs_q.count(),
                                per_page=self.PER_PAGE, bs_version=3)
        return render_template('job/status.html', jobs=jobs, status=status,
                               pagination=pagination)

    def show(self, id):
        job = Job.query.get_or_404(id)
        return render_template('job/show.html', job=job)

    @classmethod
    def register(cls, app, endpoint, url):
        status = '{}<any(completed,failed,pending):status>/'.format(url)
        view_func = cls.as_view(endpoint)
        app.add_url_rule(url, 'index', methods=['GET'], view_func=view_func)
        app.add_url_rule(status, 'status', methods=['GET'],
                         view_func=view_func)
        app.add_url_rule('{}<int:page>/'.format(status), 'status',
                         methods=['GET'], view_func=view_func)
        app.add_url_rule('%s<int:id>' % url, 'resource', methods=['GET'],
                         view_func=view_func)
