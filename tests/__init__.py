# -*- coding: utf-8 -*-
from __future__ import absolute_import
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from webtest import TestApp
from kepler.app import create_app
from kepler.extensions import db
from kepler.settings import TestConfig


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(TestConfig)
        self.ctx = app.test_request_context()
        self.ctx.push()
        self.app = TestApp(app)
        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.ctx.pop()
