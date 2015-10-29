# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class DefaultConfig(object):
    TESTING = False
    DEBUG = False
    FGDC_MODS_XSLT = os.path.join(APP_ROOT, 'templates/fgdc_to_mods.xslt')


class TestConfig(DefaultConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    GEOSERVER_PUBLIC_URL = 'http://example.com/geoserver/'
    GEOSERVER_RESTRICTED_URL = 'http://example.com/secure-geoserver/'
    GEOSERVER_WORKSPACE = 'mit'
    GEOSERVER_DATASTORE = 'data'
    OAI_ORE_URL = 'http://example.com/metadata/handle/'
    SOLR_URL = 'http://localhost:8983/solr/geoblacklight/'
    SWORD_SERVICE_URL = 'http://example.com/sword'
    SWORD_SERVICE_USERNAME = 'swordymcswordmuffin'
    SWORD_SERVICE_PASSWORD = 'vorpalblade'
    UUID_NAMESPACE = 'arrowsmith.mit.edu'
