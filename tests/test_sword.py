# -*- coding: utf-8 -*-
from __future__ import absolute_import
import xml.etree.ElementTree as ET
import tempfile
import zipfile

import pytest
from requests import HTTPError
import requests_mock

from kepler.sword import *


pytestmark = pytest.mark.usefixtures('app')


class TestSWORDPackage(object):
    def testWriteCreatesZipfile(self, grayscale_tif):
        pkg = SWORDPackage(uuid='foobar', metadata='foobaz')
        pkg.datafiles.append(grayscale_tif)
        with tempfile.TemporaryFile() as fp:
            pkg.write(fp)
            zp = zipfile.ZipFile(fp)
            assert 'mets.xml' in zp.namelist()
            assert 'grayscale.tif' in zp.namelist()


def testCreateMetsPopulatesXMLTemplate():
    mets = ET.fromstring(create_mets(uuid='frob'))
    f = mets.findall(".//{http://www.loc.gov/METS/}file")[0]
    assert f.attrib.get('ID') == 'frob'


def testSwordHeadersReturnsHeaders():
    headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'filename=dusenbury_device',
        'X-No-Op': 'false',
        'X-Packaging': 'http://purl.org/net/sword-types/METSDSpaceSIP',
    }
    assert sword_headers('dusenbury_device') == headers


def test_submit_posts_to_dspace(sword):
    submit('mock://example.com/sword', 'tests/fixtures/sword.zip')
    req = sword.request_history[0]
    assert req.url == 'mock://example.com/sword'
    assert req.text.name == 'tests/fixtures/sword.zip'


def test_submit_returns_handle(sword):
    handle = submit('mock://example.com/sword', 'tests/fixtures/sword.zip')
    assert handle == 'mit.edu:dusenbury-device:1'


def test_submit_raises_error_on_failed_submission(dspace):
    dspace.register_uri('POST', requests_mock.ANY, status_code=500)
    with pytest.raises(HTTPError):
        submit('mock://example.com/sword', 'tests/fixtures/sword.zip')
