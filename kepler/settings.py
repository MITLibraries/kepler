# -*- coding: utf-8 -*-

class DefaultConfig(object):
    TESTING = False
    DEBUG = False


class DevelopmentConfig(DefaultConfig):
    TESTING = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestConfig(DefaultConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    GEOSERVER_URL = 'http://example.com/'
