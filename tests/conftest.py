# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io

import pytest
from webtest import TestApp
from mock import patch, Mock

from kepler.app import create_app
from kepler.extensions import db as _db
from kepler.settings import TestConfig


@pytest.yield_fixture
def app():
    app = create_app(TestConfig)
    ctx = app.test_request_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture
def testapp(app):
    return TestApp(app)


@pytest.yield_fixture
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()
    yield _db
    _db.drop_all()


@pytest.yield_fixture
def bag():
    fp = io.open('tests/data/bermuda.zip', 'rb')
    yield fp
    fp.close()


@pytest.yield_fixture
def fgdc():
    fp = io.open('tests/data/shapefile/fgdc.xml', encoding='utf-8')
    yield fp
    fp.close()


@pytest.yield_fixture
def pysolr_add():
    patcher = patch('pysolr.Solr.add')
    yield patcher.start()
    patcher.stop()


@pytest.yield_fixture
def sword_service(sword):
    patcher = patch('kepler.sword.requests')
    req = patcher.start()
    req.post.return_value = Mock(text=sword)
    yield req
    patcher.stop()


@pytest.fixture
def sword():
    with io.open('tests/data/sword.xml', 'r') as fp:
        resp = fp.read()
    return resp
