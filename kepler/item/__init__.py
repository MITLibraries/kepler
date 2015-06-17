# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Blueprint

from kepler.item.views import ItemView


item_blueprint = Blueprint('item', __name__)
ItemView.register(item_blueprint, 'items', '/items/')
