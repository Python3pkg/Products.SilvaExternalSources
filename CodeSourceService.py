
import Globals
from OFS.Folder import Folder

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from Products.Silva.SilvaPermissions import ViewManagementScreens

class CodeSourceService(Folder):
    
    security = ClassSecurityInfo()
    meta_type = 'Silva Code Source Service'

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('www/serviceCodeSourceEditTab', globals())


    def __init__(self, id, title):
        self.id = id
        self.title = title


Globals.InitializeClass(CodeSourceService)

addCodeSourceService = PageTemplateFile(
    'www/serviceCodeSourceAdd', globals(),
    __name__ = 'manage_addCodeSourcesServiceForm')


def manage_addCodeSourceService(container, id, title, REQUEST=None):
    """Add a CodeSourceService object
    """
    if not title:
        title = id
    service = CodeSourceService(id, title)
    container._setObject(id, service)    
    add_and_edit(container, id, REQUEST)
    return ''
