# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from random import choice
from AccessControl import ModuleSecurityInfo

module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.codesources.make_HTML_token')

chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz-0123456789'
length = 12

module_security.declarePublic('make_token')
def make_token():
    return ''.join(choice(chars) for x in range(length))
