# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
from interfaces import IExternalSource
from ExternalSource import ExternalSource
# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.Formulator.Form import ZMIForm
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.Silva.helpers import add_and_edit

icon="www/codesource.png"

class CodeSource(ExternalSource, Folder):

    __implements__ = IExternalSource
    
    meta_type = "Silva Code Source"

    security = ClassSecurityInfo()
    
    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCodeSource'},
        ) + Folder.manage_options

    security.declareProtected(ViewManagementScreens, 'codeSourceEdit')    
    editCodeSource = PageTemplateFile(
        'www/codeSourceEdit', globals(),  __name__='editCodeSource')

    def __init__(self, id, title, script_id=None):
        CodeSource.inheritedAttribute('__init__')(self, id, title)
        self._script_id = script_id

    # ACCESSORS

    def script_id(self):
        return self._script_id

    def to_html(self, REQUEST, **kw):
        """ render HTML for code source
        """
        try:
            script = self[self._script_id]
        except KeyError:
            return None

        return script(**kw)

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editCodeSource')
    def manage_editCodeSource(
        self, title, script_id, data_encoding, description=None, cacheable=None):
        """ Edit CodeSource object
        """
        msg = ''
        if title and title != self.title:
            self.title = title
            msg += 'Title changed. '

        if script_id and script_id != self._script_id:
            self._script_id = script_id
            msg += 'Script id changed. '

        if data_encoding and data_encoding != self._data_encoding:
            self.set_data_encoding(data_encoding)
            msg += 'Data encoding changed. '

        if description and description != self._description:
            self.set_description(description)
            msg += 'Description changed. '

        if not (not not cacheable) is (not not self._is_cacheable):
            self.set_is_cacheable(cacheable)
            msg += 'Cacheability setting changed. '

        try:
            script = self[script_id]
        except KeyError:            
            msg += '<b>Warning</b>: '
            if not script_id:
                msg += 'no script id specified! '
            else:
                msg += 'This code source does not contain an callable object with id "%s"! ' % script_id

        return self.editCodeSource(manage_tabs_message=msg)

InitializeClass(CodeSource)

addCodeSource = PageTemplateFile(
    "www/codeSourceAdd", globals(), __name__='addCodeSource')

def manage_addCodeSource(context, id, title, script_id=None, REQUEST=None):
    """Add a CodeSource object
    """
    cs = CodeSource(id, title, script_id)
    context._setObject(id, cs)
    cs = context._getOb(id)
    cs.set_form(ZMIForm('form', 'Parameters form'))
    
    add_and_edit(context, id, REQUEST, screen='editCodeSource')
    return ''