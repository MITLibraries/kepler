# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import current_app
from ogre.repository import Repository


def repository(repo):
    path = current_app.config['OGM_REPOSITORIES'].get(repo)
    return Repository(path, repo)
