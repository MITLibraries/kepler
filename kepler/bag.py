# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
from zipfile import ZipFile


def read_fgdc(bag):
    archive = ZipFile(bag, 'r')
    try:
        for zf in archive.infolist():
            if zf.filename.endswith('fgdc.xml'):
                return io.BytesIO(archive.read(zf))
    finally:
        archive.close()
