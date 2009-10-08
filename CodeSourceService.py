# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements

import Globals
from OFS.Folder import Folder
from OFS.interfaces import IObjectWillBeRemovedEvent
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit, \
    register_service, unregister_service
from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.SilvaExternalSources.interfaces import ICodeSourceService

from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf

class CodeSourceService(Folder, SilvaService):

    security = ClassSecurityInfo()
    meta_type = 'Silva Code Source Service'

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('www/serviceCodeSourceEditTab', globals())

    silvaconf.icon('www/codesource_service.png')
    silvaconf.factory('manage_addCodeSourceServiceForm')
    silvaconf.factory('manage_addCodeSourceService')

    implements(ICodeSourceService)

    def __init__(self, id, title):
        self.id = id
        self.title = title

Globals.InitializeClass(CodeSourceService)

manage_addCodeSourceServiceForm = PageTemplateFile(
    'www/serviceCodeSourceAdd', globals(),
    __name__ = 'manage_addCodeSourceServiceForm')

def manage_addCodeSourceService(self, id, title, REQUEST=None):
    """Add a CodeSourceService object
    """
    if not title:
        title = id
    service = CodeSourceService(id, title)
    register_service(self, id, service, ICodeSourceService)
    add_and_edit(self, id, REQUEST)
    return ''

@silvaconf.subscribe(ICodeSourceService, IObjectWillBeRemovedEvent)
def unregisterCodeSourceService(service, event):
    unregister_service(service, ICodeSourceService)
