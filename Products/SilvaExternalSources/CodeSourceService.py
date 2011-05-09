# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$



from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from OFS.Folder import Folder

from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.SilvaExternalSources.interfaces import ICodeSourceService

from five import grok
from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf


class CodeSourceService(Folder, SilvaService):
    meta_type = 'Silva Code Source Service'

    grok.implements(ICodeSourceService)
    grok.name('service_codesources')
    silvaconf.icon('www/codesource_service.png')

    security = ClassSecurityInfo()
    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = DTMLFile('www/serviceCodeSourceEditTab', globals())


InitializeClass(CodeSourceService)
