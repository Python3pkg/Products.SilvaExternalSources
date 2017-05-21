# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import urllib.parse
import itertools


def parse_qs(qs):
    """Parse query string, like in urlparse, but do not generate list
    unless the element appears multiple times (same behavior than
    Zope).
    """
    remove_list = lambda e: e[0] if len(e) == 1 else e

    return dict(
        map(lambda k_v: (k_v[0], remove_list(k_v[1])),
                       iter(urllib.parse.parse_qs(qs, True).items())))
