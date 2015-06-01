# -*- coding: utf-8 -*-
from __future__ import absolute_import
import xml.etree.ElementTree as ET
import tempfile
import zipfile

import pytest
from mock import Mock
from requests import HTTPError

from kepler.sword import *


pytestmark = pytest.mark.usefixtures('app')


class TestSWORDPackage(object):
    def testWriteCreatesZipfile(self):
        pkg = SWORDPackage(uuid='foobar', metadata='foobaz')
        pkg.datafiles.append('tests/data/grayscale.tif')
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


def testSubmitPostsToDSpace(sword_service):
    submit('http://example.com/sword', 'tests/fixtures/sword.zip')
    args = sword_service.post.call_args[0]
    kwargs = sword_service.post.call_args[1]
    assert args[0] == 'http://example.com/sword'
    assert kwargs.get('headers') == sword_headers('sword.zip')
    assert kwargs.get('data').name == 'tests/fixtures/sword.zip'


def testSubmitReturnsHandle(sword_service):
    handle = submit('foo', 'tests/fixtures/sword.zip')
    assert handle == 'mit.edu:dusenbury-device:1'


def testSubmitRaisesErrorOnFailedSubmission(sword_service):
    sword_service.post.return_value = \
        Mock(**{'raise_for_status.side_effect': HTTPError})
    with pytest.raises(HTTPError):
        submit('foo', 'tests/fixtures/sword.zip')
