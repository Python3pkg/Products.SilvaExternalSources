# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Helpers for cs_toc...

from AccessControl import ModuleSecurityInfo

from silva.core.interfaces import IAddableContents, IPublishable

module_security = ModuleSecurityInfo('Products.SilvaExternalSources.codesources.toc')


module_security.declarePublic('get_publishable_content_types')
def get_publishable_content_types(context):
    container = context.get_container()
    return IAddableContents(container).get_all_addables(require=IPublishable)


module_security.declarePublic('get_container_content_types')
def get_container_content_types(context):
    container = context.get_container()
    return IAddableContents(container).get_container_addables()
