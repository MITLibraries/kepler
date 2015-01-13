#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask.ext.script import Manager
from kepler.app import create_app

manager = Manager(create_app())

@manager.command
def test():
    try:
        import unittest2
        suite = unittest2.defaultTestLoader.discover('tests')
        unittest2.TextTestRunner().run(suite)
    except:
        import unittest
        from colour_runner.runner import ColourTextTestRunner
        suite = unittest.defaultTestLoader.discover('tests')
        ColourTextTestRunner().run(suite)

if __name__ == '__main__':
    manager.run()
