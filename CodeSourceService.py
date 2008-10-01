# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import Globals
from OFS.Folder import Folder
from Products.Silva.BaseService import SilvaService

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from Products.Silva.SilvaPermissions import ViewManagementScreens

from silva.core import conf as silvaconf

class CodeSourceService(Folder, SilvaService):
    
    security = ClassSecurityInfo()
    meta_type = 'Silva Code Source Service'

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('www/serviceCodeSourceEditTab', globals())

    silvaconf.icon('www/codesource_service.png')
    silvaconf.factory('manage_addCodeSourceServiceForm')
    silvaconf.factory('manage_addCodeSourceService')

    def __init__(self, id, title):
        self.id = id
        self.title = title

Globals.InitializeClass(CodeSourceService)

manage_addCodeSourceServiceForm = PageTemplateFile(
    'www/serviceCodeSourceAdd', globals(),
    __name__ = 'manage_addCodeSourceServiceForm')

def manage_addCodeSourceService(container, id, title, REQUEST=None):
    """Add a CodeSourceService object
    """
    if not title:
        title = id
    service = CodeSourceService(id, title)
    container._setObject(id, service)
    add_and_edit(container, id, REQUEST)
    return ''
