#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask.ext.script import Manager
from kepler.app import create_app

manager = Manager(create_app())

if __name__ == '__main__':
    manager.run()
