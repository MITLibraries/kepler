#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from kepler.app import create_app
from kepler.settings import HerokuConfig
from kepler.extensions import db

app = create_app(HerokuConfig())

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
