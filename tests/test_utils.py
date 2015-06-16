# -*- coding: utf-8 -*-
from __future__ import absolute_import

from kepler.utils import make_uuid


def testMakeUuidReturnsUuid5():
    assert make_uuid('BD_A8GNS_2003', 'arrowsmith.mit.edu') == \
        'c8921f5a-eac7-509b-bac5-bd1b2cb202dc'
