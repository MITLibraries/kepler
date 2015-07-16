# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Blueprint

from kepler.layer.views import LayerView


layer_blueprint = Blueprint('layer', __name__)
LayerView.register(layer_blueprint, 'layer', '/layers/')
