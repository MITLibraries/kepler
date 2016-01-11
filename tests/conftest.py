# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import tempfile
import os
import shutil

import pytest
from webtest import TestApp
from mock import patch, Mock
import requests
import requests_mock

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
    """A non-authorized test application.

    Use this for GET requests that don't require authentication.
    """
    return TestApp(app)


@pytest.fixture
def auth_testapp(app):
    """An authorized test application.

    Use this for POST requests requiring authentication.
    """
    _app = TestApp(app)
    _app.authorization = ('Basic', ('username', 'password'))
    return _app


@pytest.yield_fixture
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture
def bag():
    return _fixture_path('bags/d2fe4762-96ec-57cd-89c9-312ec097284b/')


@pytest.fixture
def shapefile():
    return _fixture_path('bags/d2fe4762-96ec-57cd-89c9-312ec097284b/data/shapefile.zip')


@pytest.fixture
def bag_upload():
    return _fixture_path('bags/d2fe4762-96ec-57cd-89c9-312ec097284b.zip')


@pytest.fixture
def bag_tif_upload():
    return _fixture_path('bags/674a0ab1-325f-561a-a837-09e9a9a79b91.zip')


@pytest.fixture
def bag_tif():
    return _fixture_path('bags/674a0ab1-325f-561a-a837-09e9a9a79b91/')


@pytest.fixture
def grayscale_tif():
    return _fixture_path('grayscale.tif')


@pytest.fixture
def rgb_tif():
    return _fixture_path('rgb.tif')


@pytest.fixture
def paletted_tif():
    return _fixture_path('paletted.tif')


@pytest.fixture
def marc():
    return _fixture_path('marc.xml')


@pytest.fixture
def marc_bad034():
    return _fixture_path('marc_bad034.xml')


@pytest.fixture
def marc_really_bad034():
    return _fixture_path('marc_really_bad034.xml')


@pytest.fixture
def fgdc(bag):
    return os.path.join(bag, 'data/fgdc.xml')


@pytest.fixture
def oai_ore():
    with io.open(_fixture_path('oai_ore.xml'), 'r') as fp:
        resp = fp.read()
    return resp


@pytest.fixture
def oai_ore_no_tiffs():
    with io.open(_fixture_path('oai_ore_no_tiffs.xml'), 'r') as fp:
        resp = fp.read()
    return resp


@pytest.fixture
def oai_ore_two_tiffs():
    with io.open(_fixture_path('oai_ore_two_tiffs.xml'), 'r') as fp:
        resp = fp.read()
    return resp


@pytest.yield_fixture
def pysolr():
    adapter = requests_mock.Adapter()
    patcher = patch('kepler.solr_session', new_callable=requests.Session)
    sess = patcher.start()
    sess.mount('mock', adapter)
    yield adapter
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
    with io.open(_fixture_path('sword.xml'), 'r') as fp:
        resp = fp.read()
    return resp


def _fixture_path(path):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'fixtures', path)
