# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Blueprint

from kepler.marc.views import MarcView


marc_blueprint = Blueprint('marc', __name__)
MarcView.register(marc_blueprint, 'marc', '/marc/')
