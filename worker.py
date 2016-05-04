# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import os

import redis
from rq import Connection, Worker, Queue

from kepler.app import create_app
from kepler.settings import HerokuConfig


redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)


if __name__ == '__main__':
    app = create_app(HerokuConfig())
    with app.app_context():
        with Connection(conn):
            worker = Worker(Queue())
            worker.work()
