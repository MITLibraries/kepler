# -*- coding: utf-8 -*-
from __future__ import absolute_import


class UnsupportedFormat(Exception):
    status_code = 415

    def __init__(self, mimetype):
        self.mimetype = mimetype


class FileNotFound(Exception):
    pass


class InvalidAccessLevel(Exception):
    pass
