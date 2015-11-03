# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import abort, current_app, request


def authenticate_client(username, password):
    return "%s:%s" % (username, password) == \
        current_app.config.get('CLIENT_AUTH')


def client_auth_required(f):
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate_client(auth.username, auth.password):
            abort(401)
        return f(*args, **kwargs)
    return wrapper
