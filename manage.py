#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.ext.script import Manager, Server

from kepler.app import create_app
from kepler.extensions import db


manager = Manager(create_app())
manager.add_command("runserver", Server())


@manager.command
def dropdb():
    db.drop_all()


@manager.command
def createdb():
    db.create_all()


if __name__ == '__main__':
    manager.run()
