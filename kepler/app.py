# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging.config
import os

from flask import Flask
import yaml
import rq_dashboard

from kepler.extensions import db, solr, geoserver, dspace, req, s3
from kepler.job import job_blueprint
from kepler.item import item_blueprint
from kepler.layer import layer_blueprint
from kepler.marc import marc_blueprint
from kepler.settings import DefaultConfig


def create_app(cfg_obj=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DefaultConfig)
    app.config.from_object(cfg_obj)

    register_loggers(app)
    register_extensions(app)
    register_blueprints(app)
    app.logger.info('Application Startup Complete')
    return app


def register_extensions(app):
    db.init_app(app)
    solr.init_app(app)
    geoserver.init_app(app)
    dspace.init_app(app)
    req.init_app(app)
    s3.init_app(app)
    app.logger.info('Extensions registered')


def register_blueprints(app):
    app.register_blueprint(job_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(layer_blueprint)
    app.register_blueprint(marc_blueprint)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/rq')
    app.logger.info('Blueprints registered')


def register_loggers(app):
    logging_config = os.getenv('LOGGING_CONFIG', 'kepler/logging.conf')
    with open(logging_config) as f:
        logging.config.dictConfig(yaml.load(f))
    app.logger.info('Loggers registered')
