# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import Flask
from .extensions import db
from .ingest import ingest_blueprint
from .settings import DefaultConfig
from .exceptions import UnsupportedFormat

def create_app(cfg_obj=None):
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    # Load any config from provided object
    app.config.from_object(cfg_obj)

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    db.init_app(app)


def register_blueprints(app):
    app.register_blueprint(ingest_blueprint)


def register_errorhandlers(app):
    def handle_unsupported_format(error):
        return '', 415
    app.errorhandler(UnsupportedFormat)(handle_unsupported_format)
