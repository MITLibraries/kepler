# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import reduce


def compose(*funcs):
    return reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)),
                  funcs)
