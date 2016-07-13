# -*- coding: utf-8 -*-
from __future__ import absolute_import
import uuid

from flask import request


def make_uuid(value, namespace):
    ns = uuid.uuid5(uuid.NAMESPACE_DNS, namespace)
    uid = uuid.uuid5(ns, value)
    return str(uid)


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > request.accept_mimetypes['text/html']
