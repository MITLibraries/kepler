# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from kepler.app import create_app
from kepler.extensions import req
from kepler.settings import HerokuConfig
from kepler.tasks import resolve_pending_jobs


if __name__ == '__main__':
    app = create_app(HerokuConfig())
    with app.app_context():
        req.q.enqueue(resolve_pending_jobs)
