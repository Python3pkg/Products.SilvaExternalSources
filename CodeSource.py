# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva Interfaces
from Silva.interfaces import IExternalSource
# Silva
from Silva.SilvaPermissions import ViewManagementScreens
from Silva.ExternalSource import ExternalSource

icon="www/codesource.png"

class CodeSource(Folder, ExternalSource):

    __implements__ = IExternalSource
    
    meta_type = "Silva Code Source"

    security = ClassSecurityInfo()

    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCodeSource'},
        {'label':'Parameters', 'action':'form'},
        {'label':'Preview', 'action':'previewCodeSource'},
        ) + Folder.manage_options

    security.declareProtected(ViewManagementScreens, 'editCodeSource')
    editCodeSource = PageTemplateFile(
        'www/editCodeSource', globals(),  __name__='editCodeSource')

    security.declareProtected(ViewManagementScreens, 'previewCodeSource')
    previewCodeSource = PageTemplateFile(
        'www/previewCodeSource', globals(),  __name__='previewCodeSource')

    def __init__(self, id, title):
        CodeSource.inheritedAttribute('__init__')(self, id, title)
        self._script_id = None        

    # MANAGERS

    def manage_editCodeSource(self, **kw):
        return self.editCodeSource(manage_tabs_message='')

InitializeClass(CodeSource)

