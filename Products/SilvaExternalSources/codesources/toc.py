# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Helpers for cs_toc...

from AccessControl import ModuleSecurityInfo
import zope.deferredimport

module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.codesources.toc')
module_security.declarePublic('get_publishable_content_types')
module_security.declarePublic('get_container_content_types')

zope.deferredimport.deprecated(
    'Please refresh your TOC code source',
    get_publishable_content_types='Products.SilvaExternalSources.codesources.api:get_publishable_content_types',
    get_container_content_types='Products.SilvaExternalSources.codesources.api:get_container_content_types')


