# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Blueprint

from kepler.job.views import JobView


job_blueprint = Blueprint('job', __name__)
JobView.register(job_blueprint, 'job', '/job/')
