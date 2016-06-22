# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class DefaultConfig(object):
    TESTING = False
    DEBUG = False
    FGDC_MODS_XSLT = os.path.join(APP_ROOT, 'templates/fgdc_to_mods.xslt')


class HerokuConfig(DefaultConfig):
    def __init__(self):
        self.CLIENT_AUTH = os.environ['CLIENT_AUTH']
        self.SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
        self.SECRET_KEY = os.environ['SECRET_KEY']
        self.GEOSERVER_PUBLIC_URL = os.environ['GEOSERVER_PUBLIC_URL']
        self.GEOSERVER_RESTRICTED_URL = os.environ['GEOSERVER_RESTRICTED_URL']
        self.GEOSERVER_WORKSPACE = os.environ['GEOSERVER_WORKSPACE']
        self.GEOSERVER_DATASTORE = os.environ['GEOSERVER_DATASTORE']
        self.SOLR_URL = os.environ['SOLR_URL']
        self.SOLR_AUTH_USER = os.environ['SOLR_AUTH_USER']
        self.SOLR_AUTH_PASS = os.environ['SOLR_AUTH_PASS']
        self.OAI_ORE_URL = os.environ['OAI_ORE_URL']
        self.SWORD_SERVICE_URL = os.environ['SWORD_SERVICE_URL']
        self.SWORD_SERVICE_USERNAME = os.environ['SWORD_SERVICE_USERNAME']
        self.SWORD_SERVICE_PASSWORD = os.environ['SWORD_SERVICE_PASSWORD']
        self.UUID_NAMESPACE = os.environ['UUID_NAMESPACE']
        self.GEOSERVER_AUTH_USER = os.environ['GEOSERVER_AUTH_USER']
        self.GEOSERVER_AUTH_PASS = os.environ['GEOSERVER_AUTH_PASS']
        self.REDISTOGO_URL = os.environ['REDISTOGO_URL']
        self.REDIS_URL = os.environ['REDISTOGO_URL']
        self.RQ_POLL_INTERVAL = 2500


class TestConfig(DefaultConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    GEOSERVER_PUBLIC_URL = 'mock://example.com/geoserver/'
    GEOSERVER_RESTRICTED_URL = 'mock://secure.example.com/geoserver/'
    GEOSERVER_WORKSPACE = 'mit'
    GEOSERVER_DATASTORE = 'data'
    OAI_ORE_URL = 'mock://example.com/metadata/handle/'
    SOLR_URL = 'mock://localhost:8983/solr/geoblacklight/'
    SWORD_SERVICE_URL = 'mock://example.com/sword'
    SWORD_SERVICE_USERNAME = 'swordymcswordmuffin'
    SWORD_SERVICE_PASSWORD = 'vorpalblade'
    UUID_NAMESPACE = 'arrowsmith.mit.edu'
    CLIENT_AUTH = 'username:password'
    GEOSERVER_AUTH_USER = 'username'
    GEOSERVER_AUTH_PASS = 'password'
    REDISTOGO_URL = 'redis://localhost:6379'
