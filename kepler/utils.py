# -*- coding: utf-8 -*-
from __future__ import absolute_import
import uuid


def make_uuid(value, namespace):
    ns = uuid.uuid5(uuid.NAMESPACE_DNS, namespace)
    uid = uuid.uuid5(ns, value)
    return str(uid)
