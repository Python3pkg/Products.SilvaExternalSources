# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.Formulator.Form import ZMIForm
from Products.SilvaExternalSources.interfaces import ICodeSource
from Products.SilvaExternalSources.ExternalSource import EditableExternalSource
from Products.Silva.SilvaPermissions import ViewManagementScreens, \
    AccessContentsInformation
from Products.Silva.helpers import add_and_edit

from five import grok
from silva.core.interfaces.content import IVersion
from silva.core.services.base import ZMIObject
from silva.core import conf as silvaconf


class CodeSource(EditableExternalSource, Folder, ZMIObject):

    grok.implements(ICodeSource)

    meta_type = "Silva Code Source"
    security = ClassSecurityInfo()

    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCodeSource'},
        ) + Folder.manage_options

    security.declareProtected(ViewManagementScreens, 'editCodeSource')
    editCodeSource = PageTemplateFile(
        'www/codeSourceEdit', globals(),  __name__='editCodeSource')

    # register icon and factories
    silvaconf.icon('www/codesource.png')
    silvaconf.factory('manage_addCodeSourceForm')
    silvaconf.factory('manage_addCodeSource')

    _data_encoding = 'UTF-8'

    def __init__(self, id, script_id=None):
        super(CodeSource, self).__init__(id)
        self._script_id = script_id

    def is_broken(self):
        # return True if the source is broken and needs maintenance.
        if self.parameters is not None:
            try:
                self.parameters.get_fields()
            except AttributeError:
                return True
        return False

    # ACCESSORS
    security.declareProtected(AccessContentsInformation, 'script_id')
    def script_id(self):
        return self._script_id

    security.declareProtected(AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """Render HTML for code source
        """
        try:
            script = self[self._script_id]
        except KeyError:
            return None
        parameters['version'] = None
        parameters['model'] = content.get_content()
        if IVersion.providedBy(content):
            parameters['version'] = content
        result = script(**parameters)
        if isinstance(result,  unicode):
            return result
        return unicode(result, self.get_data_encoding(), 'replace')

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editCodeSource')
    def manage_editCodeSource(
        self, title, script_id, data_encoding, description=None,
        cacheable=None, previewable=None):
        """ Edit CodeSource object
        """
        msg = u''

        if data_encoding and data_encoding != self._data_encoding:
            try:
                unicode('abcd', data_encoding, 'replace')
            except LookupError:
                # unknown encoding, return error message
                msg += "Unknown encoding %s, not changed! " % data_encoding
                return self.editCodeSource(manage_tabs_message=msg)
            self.set_data_encoding(data_encoding)
            msg += u'Data encoding changed. '

        title = unicode(title, self.management_page_charset)

        if title and title != self.title:
            self.title = title
            msg += "Title changed. "

        if script_id and script_id != self._script_id:
            self._script_id = script_id
            msg += "Script id changed. "

        # Assume description is in the encoding as specified
        # by "management_page_charset". Store it in unicode.
        description = unicode(description, self.management_page_charset)

        if description != self._description:
            self.set_description(description)
            msg += "Description changed. "

        if not (not not cacheable) is (not not self._is_cacheable):
            self.set_cacheable(cacheable)
            msg += "Cacheability setting changed. "

        if not (not not previewable) is (not not self.is_previewable()):
            self.set_previewable(previewable)
            msg += "Previewable setting changed. "

        if not script_id:
            msg += "<b>Warning</b>: no script id specified!"
        if script_id not in self.objectIds():
            msg += '<b>Warning</b>: This code source does not contain ' \
                'an object with identifier "%s"! ' % script_id
        return self.editCodeSource(manage_tabs_message=msg)

InitializeClass(CodeSource)


manage_addCodeSourceForm = PageTemplateFile(
    "www/codeSourceAdd", globals(),
    __name__='manage_addCodeSourceForm')


def manage_addCodeSource(context, id, title, script_id=None, REQUEST=None):
    """Add a CodeSource object
    """
    cs = CodeSource(id, script_id)
    title = unicode(title, cs.management_page_charset)
    cs.title = title
    context._setObject(id, cs)
    cs = context._getOb(id)
    cs.set_form(ZMIForm('form', 'Parameters form', unicode_mode=1))

    add_and_edit(context, id, REQUEST, screen='editCodeSource')
    return ''
