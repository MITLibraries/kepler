# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import tempfile
import os
import shutil

import pytest
from webtest import TestApp
from mock import patch, Mock

from kepler.app import create_app
from kepler.extensions import db as _db
from kepler.settings import TestConfig


@pytest.yield_fixture(scope="session", autouse=True)
def temp_dir():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = tempfile.mkdtemp(dir=current_dir)
    tempfile.tempdir = tmp_dir
    yield
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)


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


@pytest.fixture
def bag():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'data/bermuda/')


@pytest.fixture
def shapefile():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'data/bermuda/data/shapefile.zip')


@pytest.fixture
def bag_upload():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'data/bermuda.zip')


@pytest.fixture
def marc():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'data/marc.xml')


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
