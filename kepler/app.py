# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import Flask
from .extensions import db
from kepler.job import job_blueprint
from kepler.item import item_blueprint
from kepler.layer import layer_blueprint
from kepler.marc import marc_blueprint
from .settings import DefaultConfig
from .exceptions import UnsupportedFormat


def create_app(cfg_obj=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DefaultConfig)
    app.config.from_object(cfg_obj)

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    db.init_app(app)


def register_blueprints(app):
    app.register_blueprint(job_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(layer_blueprint)
    app.register_blueprint(marc_blueprint)


def register_errorhandlers(app):
    def handle_unsupported_format(error):
        return '', 415
    app.errorhandler(UnsupportedFormat)(handle_unsupported_format)
