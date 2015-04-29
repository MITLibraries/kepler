# -*- coding: utf-8 -*-
from __future__ import absolute_import
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import os.path
import io

import arrow
import requests
from flask import current_app


class SWORDPackage(object):
    """A SWORD Package.

    This provids a container for the metadata and data files comprising a
    SWORD package. Use the :func:`~kepler.sword.SWORDPackage.write` method
    to serialize the package::

        from kepler.sword import SWORDPackage

        pkg = SWORDPackage(uuid='1234', metadata='<xml...>')
        pkg.datafiles.append('some/data/file.tif')
        pkg.write('sword.zip')

    :param uuid: file uuid
    :param metadata: metadata string to be added to mods record
    :param datafiles: list of filenames to be added to SWORD package
    """

    def __init__(self, uuid, metadata=None, datafiles=[]):
        self.uuid = uuid
        self.metadata = metadata
        self.datafiles = datafiles

    def write(self, file):
        """Serialize the SWORD package.

        :param file: file name or file pointer to write package to
        """

        datafile = self.datafiles[0]
        filename = os.path.basename(datafile)
        mets = create_mets(uuid=self.uuid, file_path=filename,
                           metadata=self.metadata,
                           create_date=arrow.utcnow().isoformat())
        pkg = ZipFile(file, 'w')
        try:
            pkg.writestr('mets.xml', mets.encode('utf-8'))
            pkg.write(datafile, filename)
        finally:
            pkg.close()


def submit(service, package):
    """Submit a SWORD package.

    Submits the given package to the specified SWORD service. If the submission
    was successful, the handle of the created resource will be returned.

    :param service: URL for SWORD service
    :param package: path to SWORD package on file system
    """

    headers = sword_headers(os.path.basename(package))
    with io.open(package, 'rb') as fp:
        r = requests.post(service, data=fp, headers=headers)
    r.raise_for_status()
    doc = ET.fromstring(r.text)
    handle = doc.find('.//{http://www.w3.org/2005/Atom}id').text
    return handle


def create_mets(**kwargs):
    """Create a METS file for inclusion in SWORD package.

    This will look for a ``mets.xml`` template in the current app's template
    directory and apply the supplied ``kwargs`` as a context.

    :param kwargs: context for METS template
    """

    env = current_app.jinja_env
    tmpl = env.get_template('mets.xml')
    return tmpl.render(**kwargs)


def sword_headers(filename):
    """Returns SWORD headers for specified package.

    :params filename: name of SWORD package
    """

    return {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'filename=%s' % filename,
        'X-No-Op': 'false',
        'X-Packaging': 'http://purl.org/net/sword-types/METSDSpaceSIP',
    }
