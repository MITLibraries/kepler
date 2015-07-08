# -*- coding: utf-8 -*-


class DefaultConfig(object):
    TESTING = False
    DEBUG = False


class TestConfig(DefaultConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    GEOSERVER_PUBLIC_URL = 'http://example.com/geoserver/'
    GEOSERVER_RESTRICTED_URL = 'http://example.com/secure-geoserver/'
    GEOSERVER_WORKSPACE = 'mit'
    GEOSERVER_DATASTORE = 'data'
    SOLR_URL = 'http://localhost:8983/solr/geoblacklight/'
    SWORD_SERVICE_URL = 'http://example.com/sword'
    SWORD_SERVICE_USERNAME = 'swordymcswordmuffin'
    SWORD_SERVICE_PASSWORD = 'vorpalblade'
    UUID_NAMESPACE = 'arrowsmith.mit.edu'
