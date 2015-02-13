# -*- coding: utf-8 -*-
from __future__ import absolute_import

class UnsupportedFormat(Exception):
    status_code = 415

    def __init__(self, mimetype):
        self.mimetype = mimetype


class InvalidDataError(Exception):
    def __init__(self, field, value):
        super(InvalidDataError, self).__init__(field, value)
        self.field = field
        self.value = value
