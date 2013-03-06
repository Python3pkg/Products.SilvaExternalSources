# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import urlparse
import itertools


def parse_qs(qs):
    """Parse query string, like in urlparse, but do not generate list
    unless the element appears multiple times (same behavior than
    Zope).
    """
    remove_list = lambda e: e[0] if len(e) == 1 else e

    return dict(
        itertools.imap(lambda (k, v): (k, remove_list(v)),
                       urlparse.parse_qs(qs, True).iteritems()))
