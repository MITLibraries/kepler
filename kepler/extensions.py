# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask.ext.sqlalchemy import SQLAlchemy
import requests

from kepler.geoserver import GeoService


class BaseExtension(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        raise NotImplementedError


class Solr(BaseExtension):
    def init_app(self, app):
        auth = (app.config.get('SOLR_AUTH_USER'),
                app.config.get('SOLR_AUTH_PASS'))
        self.session = requests.Session()
        self.session.auth = auth


class GeoServer(BaseExtension):
    def init_app(self, app):
        auth = (app.config.get('GEOSERVER_AUTH_USER'),
                app.config.get('GEOSERVER_AUTH_PASS'))
        pub_session = requests.Session()
        pub_session.auth = auth
        sec_session = requests.Session()
        sec_session.auth = auth
        self._public = GeoService(
            session=pub_session,
            url=app.config.get('GEOSERVER_PUBLIC_URL'),
            workspace=app.config.get('GEOSERVER_WORKSPACE'),
            datastore=app.config.get('GEOSERVER_DATASTORE'))
        self._secure = GeoService(
            session=sec_session,
            url=app.config.get('GEOSERVER_RESTRICTED_URL'),
            workspace=app.config.get('GEOSERVER_WORKSPACE'),
            datastore=app.config.get('GEOSERVER_DATASTORE'))

    @property
    def public(self):
        return self._public

    @property
    def secure(self):
        return self._secure


class DSpace(BaseExtension):
    def init_app(self, app):
        auth = (app.config.get('SWORD_SERVICE_USERNAME'),
                app.config.get('SWORD_SERVICE_PASSWORD'))
        self.session = requests.Session()
        self.session.auth = auth


db = SQLAlchemy()
solr = Solr()
geoserver = GeoServer()
dspace = DSpace()
