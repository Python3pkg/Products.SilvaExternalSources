# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.15 $
from interfaces import IExternalSource
from ExternalSource import ExternalSource
# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.Formulator.Form import ZMIForm
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens, AccessContentsInformation
from Products.Silva.helpers import add_and_edit
from Products.Silva.i18n import translate as _

icon="www/codesource.png"

class CodeSource(ExternalSource, Folder):

    __implements__ = IExternalSource
    
    meta_type = "Silva Code Source"

    security = ClassSecurityInfo()

    # UTF as UI is in UTF-8
    _data_encoding = 'UTF-8'
        
    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCodeSource'},
        ) + Folder.manage_options

    security.declareProtected(AccessContentsInformation, 'get_rendered_form_for_editor')
    security.declareProtected(AccessContentsInformation, 'validate_form_to_request')

    security.declareProtected(ViewManagementScreens, 'editCodeSource')
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
        result = script(**kw)
        if type(result) is unicode:
            return result
        return unicode(result, self.data_encoding())
    
    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editCodeSource')
    def manage_editCodeSource(
        self, title, script_id, data_encoding, description=None, cacheable=None):
        """ Edit CodeSource object
        """
        msg = u''

        if data_encoding and data_encoding != self._data_encoding:
            try:
                unicode('abcd', data_encoding, 'replace')
            except LookupError:
                # unknown encoding, return error message
                m = _("Unknown encoding ${enc}, not changed! ")
                m.set_mapping({"enc":charset})
                sm = unicode(m)
                msg += sm #"Unknown encoding %s, not changed!. " % data_encoding
                return self.editCodeSource(manage_tabs_message=msg)
            self.set_data_encoding(data_encoding)
            msg += 'Data encoding changed. '

        if title and title != self.title:
            self.title = title
            m = _("Title changed. ")
            sm = unicode(m)
            msg += sm #'Title changed. '

        if script_id and script_id != self._script_id:
            self._script_id = script_id
            m = _("Script id changed. ")
            sm = unicode(m)
            msg += sm #'Script id changed. '

        # Assume description is in the encoding as specified 
        # by "management_page_charset". Store it in unicode.
        description = unicode(
            description, self.management_page_charset, 'replace')

        if description != self._description:
            self.set_description(description)
            m = _("Description changed. ")
            sm = unicode(m)
            msg += sm #'Description changed. '

        if not (not not cacheable) is (not not self._is_cacheable):
            self.set_is_cacheable(cacheable)
            m = _("Cacheability setting changed. ")
            sm = unicode(m)
            msg += sm #'Cacheability setting changed. '

        try:
            script = self[script_id]
        except KeyError:            
            m = _("<b>Warning</b>: ")
            sm = unicode(m)
            msg += sm #'<b>Warning</b>: '
            if not script_id:
                m = _('no script id specified! ')
            else:
                m = _('This code source does not contain an callable object with id "${id}"! ')
                m.set_mapping({'id': script_id})
            sm = unicode(m)
            msg += sm

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
