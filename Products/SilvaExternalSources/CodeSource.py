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


_marker = object()

def cast_formulator_value(value, field_type):
    if field_type == 'CheckBoxField':
        if value is not None and int(value)==1:
            return True
        return False
    elif field_type == 'IntegerField':
        if not value: #if value is not set
            return None
        return int(value)
    elif field_type == 'MultiListField':
        if not value:
            return []
        if not isinstance(value, list):
            return eval(value)
        return value
    #XXX More field types? Dates? Selects?
    return value


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
    _elaborate = False

    def __init__(self, id, script_id=None):
        super(CodeSource, self).__init__(id)
        self._script_id = script_id
        self._icon_id = None

    # ACCESSORS

    security.declareProtected(AccessContentsInformation, 'is_elaborate')
    def is_elaborate(self):
        return self._elaborate

    security.declareProtected(AccessContentsInformation, 'script_id')
    def script_id(self):
        return self._script_id

    security.declareProtected(AccessContentsInformation, 'icon_id')
    def icon_id(self):
        if not hasattr(self, '_icon_id'):
            self._icon_id = None
        return self._icon_id
    
    security.declareProtected(AccessContentsInformation, 'get_icon')
    def get_icon(self):
        if not self.icon_id():
            return None
        try:
            return self[self._icon_id]
        except KeyError:
            return None

    security.declareProtected(AccessContentsInformation,
                                'get_rendered_form_for_editor')
    def get_rendered_form_for_editor(self, REQUEST=None):
        """non empty docstring"""
        html = super(CodeSource, self).get_rendered_form_for_editor(REQUEST)
        if self.is_elaborate():
            root_url = self.get_root_url()
            html = html.replace(
                '<form ', '<html><head>'
                '<style media="all" type="text/css" xml:space="preserve">'
                '@import url(%s);</style>'
                '<link href="%s" rel="stylesheet" type="text/css" />'
                '<link href="%s" type="text/css" rel="stylesheet" />'
                '</head><body><div class="kupu-toolbox-active"><div'
                ' class="kupu-tooltray"><div '
                'id="kupu-extsource-formcontainer"><form class="elaborate" '
                % (root_url + '/++resource++silva.core.smi/smi.css',
                   root_url + '/globals/silvaContentStyle.css',
                   'kupustyles.css',))
            html = html.replace(
                '</form>', '<input name="update_button" type="button"'
                ' class="button" value="update"'
                ' onClick="window.opener.kupu.tools.extsourcetool._form='
                'window.document.forms[0];window.opener.kupu.tools.'
                'extsourcetool._validateAndSubmit(true);window.close()">'
                '</form></div></div><div></body></html>')
        return html

    security.declareProtected(AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """Render HTML for code source
        """
        try:
            script = self[self._script_id]
        except KeyError:
            return None
        self._prepare_parameters(parameters)
        parameters['version'] = None
        parameters['model'] = content.get_content()
        if IVersion.providedBy(content):
            parameters['version'] = content
        result = script(**parameters)
        if type(result) is unicode:
            return result
        return unicode(result, self.get_data_encoding(), 'replace')

    def _prepare_parameters(self, parameters):
        form = self.get_parameters_form()
        if form is None:
            return parameters
        for field in form.get_fields():
            value = parameters.get(field.id, _marker)
            if value is _marker:
                value = field.get_value('default')
            parameters[field.id] = cast_formulator_value(value, field.meta_type)
        return parameters

    def set_elaborate(self, value):
        self._elaborate = value

        
    def set_icon_id(self, icon_id):
        #XXX should probably have some validation here
        self._icon_id = icon_id

# MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editCodeSource')
    def manage_editCodeSource(
        self, title, script_id, data_encoding, description=None,
        cacheable=None, elaborate=None, previewable=None, priority=None, 
        icon_id=None):
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

        if icon_id and icon_id != self._icon_id:
            self._icon_id = icon_id
            msg += "Icon id changed. "

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

        if not elaborate:
            if self.is_elaborate():
                self.set_elaborate(False)
        elif not self.is_elaborate():
            self.set_elaborate(True)

        if priority != self.priority():
            self.set_priority(priority)
            msg += 'Priority changed. '

        if not script_id:
            msg += "<b>Warning</b>: no script id specified!"
        if script_id not in self.objectIds():
            msg += '<b>Warning</b>: This code source does not contain ' \
                'an object with identifier "%s"! ' % script_id
        if icon_id not in self.objectids():
            msg += '<b>Warning</b>: This code source does not contain ' \
                'an object with identifier "%s"! ' % icon_id
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
