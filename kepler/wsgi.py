# -*- coding: utf-8 -*-
from kepler.app import create_app
from kepler.settings import HerokuConfig

application = create_app(HerokuConfig())
