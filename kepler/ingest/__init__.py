# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import Blueprint
from .views import IngestView

ingest_blueprint = Blueprint('ingest', __name__)
IngestView.register(ingest_blueprint, 'ingest', '/ingest/')
