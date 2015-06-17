# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import request, render_template
from flask.views import View

from kepler.models import Item, Job


class ItemView(View):
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if request.endpoint.endswith('.index'):
                return self.list()
            return self.show(*args, **kwargs)

    def list(self):
        items = Item.query.all()
        return render_template('item/index.html', items=items)

    def show(self, id):
        item = Item.query.get_or_404(id)
        jobs = item.jobs.order_by(Job.time.desc())
        return render_template('item/show.html', item=item, jobs=jobs)

    @classmethod
    def register(cls, app, endpoint, url):
        view_func = cls.as_view(endpoint)
        app.add_url_rule(url, 'index', methods=['GET'], view_func=view_func)
        app.add_url_rule('%s<path:id>' % url, 'resource', methods=['GET'],
                         view_func=view_func)
