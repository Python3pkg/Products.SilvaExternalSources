# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from operator import itemgetter
import cgi
import io
import os
import shutil
import tempfile
import zipfile

# Zope
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.Formulator.Form import ZMIForm
from Products.SilvaExternalSources.interfaces import ICodeSource
from Products.SilvaExternalSources.interfaces import ICodeSourceService
from Products.SilvaExternalSources.ExternalSource import EditableExternalSource
from Products.Silva.SilvaPermissions import ViewManagementScreens, \
    AccessContentsInformation
from Products.Silva.helpers import add_and_edit

from five import grok
from zope.component import queryUtility
from zope.publisher.interfaces.browser import IBrowserSkinType

from silva.core.interfaces.content import IVersion
from silva.core.services.base import ZMIObject
from silva.core import conf as silvaconf


class CodeSourceErrorSupplement(object):
    """Add more information about an error happening during the
    rendering of a code source.
    """

    def __init__(self, source, parameters):
        self.source = source
        self.parameters = parameters

    def getInfo(self, as_html=0):
        info = list()
        info.append((u'Source path', '/'.join(self.source.getPhysicalPath())))
        if 'model' in self.parameters:
            document = self.parameters['model']
            info.append((u'Document type', document.meta_type))
            info.append((u'Document path', '/'.join(document.getPhysicalPath())))
        if 'version' in self.parameters:
            version = self.parameters['version']
            info.append((u'Document version', version.getId()))
        for name, value in self.parameters.items():
            if name not in ('model', 'version'):
                info.append((u'Parameter %s' % name, repr(value)))

        if not as_html:
            return '   - ' + '\n   - '.join(map(lambda x: '%s: %s' % x, info))

        return u'<p>Extra information:<br /><li>%s</li></p>' % ''.join(map(
                lambda x: u'<li><b>%s</b>: %s</li>' % (
                    cgi.escape(str(x[0])), cgi.escape(str(x[1]))),
                info))


class CodeSource(EditableExternalSource, Folder, ZMIObject):
    grok.implements(ICodeSource)
    # register icon and factories
    silvaconf.icon('www/codesource.png')
    silvaconf.factory('manage_addCodeSourceForm')
    silvaconf.factory('manage_addCodeSource')
    silvaconf.zmi_addable(True)

    meta_type = "Silva Code Source"
    security = ClassSecurityInfo()

    _data_encoding = 'UTF-8'
    _fs_location = None
    _script_layers = []

    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCodeSource'},
        {'label':'Parameters', 'action':'parameters/manage_main'},
        ) + Folder.manage_options
    management_page_charset = 'utf-8'

    security.declareProtected(ViewManagementScreens, 'editCodeSource')
    editCodeSource = PageTemplateFile(
        'www/codeSourceEdit', globals(),  __name__='editCodeSource')


    def __init__(self, id, script_id=None, fs_location=None):
        super(CodeSource, self).__init__(id)
        self._script_id = script_id
        self._fs_location = fs_location

    security.declareProtected(ViewManagementScreens, 'test_source')
    def test_source(self):
        # return a list of problems or None
        errors = []
        # in real life the parent of the form is the document. We try
        # to do the same here.
        root = self.get_root()
        if root.get_default():
            root = root.get_default()
        if self.parameters is not None:
            try:
                self.parameters.test_form(
                    context=root,
                    bad_fields=['context', 'content', 'model', 'script'])
            except ValueError as error:
                errors.extend(error.args)
        if not self.title:
            errors.append(u'Missing required source title.')
        if not self._script_id:
            errors.append(u'Missing required renderer id.')
        else:
            ids = self.objectIds()
            scripts = [self._script_id] + map(
                itemgetter(0), self._script_layers)
            for script_id in scripts:
                if script_id not in ids:
                    errors.append(
                        u'Missing renderer %s. Please a script or template with this id.' % (
                            script_id))
        if errors:
            return errors
        return None

    security.declareProtected(AccessContentsInformation, 'get_icon')
    def get_icon(self):
        return self._getOb('icon.png', None)

    # ACCESSORS
    security.declareProtected(AccessContentsInformation, 'get_script_id')
    def get_script_id(self):
        return self._script_id

    security.declareProtected(AccessContentsInformation, 'get_script_layers')
    def get_script_layers(self):
        result = []
        skin = grok.skin.bind(default=lambda l: l.__identifier__)
        for script_id, layer in self._script_layers:
            result.append(":".join((script_id, skin.get(layer))))
        return '\n'.join(result)

    security.declareProtected(AccessContentsInformation, 'get_fs_location')
    def get_fs_location(self):
        return self._fs_location

    security.declareProtected(AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """Render HTML for code source
        """
        script = None
        if self._script_layers:
            # If there are script_layer, check them first.
            for script_id, layer in self._script_layers:
                if layer.providedBy(request):
                    break
            else:
                # No matching layer, default.
                script_id = self._script_id
        else:
            # No script_layer, default one.
            script_id = self._script_id
        if script_id is not None:
            script = self._getOb(script_id, None)
        if script_id is None or script is None:
            # Missing script
            return None
        parameters['REQUEST'] = request
        if IVersion.providedBy(content):
            parameters['version'] = content
            parameters['model'] = content.get_silva_object()
        else:
            parameters['version'] = None
            parameters['model'] = content
        __traceback_supplement__ = (CodeSourceErrorSupplement, self, parameters)
        result = script(**parameters)
        if isinstance(result,  unicode):
            return result
        return unicode(result, self.get_data_encoding(), 'replace')

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'set_script_id')
    def set_script_id(self, script_id):
        self._script_id = script_id

    security.declareProtected(ViewManagementScreens, 'set_script_layers')
    def set_script_layers(self, script_layers):
        found = []
        for lineno, line in enumerate(script_layers.strip().splitlines()):
            entries = line.strip().split(':', 1)
            if len(entries) != 2:
                raise ValueError(
                    u'Invalid script layers: invalid form on line %d' % (
                        lineno))
            script_id, layer_identifier = entries
            layer = queryUtility(IBrowserSkinType, name=layer_identifier)
            if layer is None:
                raise ValueError(
                    u'Invalid script layer: layer %s not found on line %d' % (
                        layer_identifier, lineno))
            found.append((script_id, layer))
        self._script_layers = found

    def _get_installable(self, location=None):
        """Return the installable source associated with this code
        source.
        """
        if location is None:
            location = self.get_fs_location()
            if location is None:
                return None
        service = queryUtility(ICodeSourceService)
        if service is None:
            # XXX pre-migration Silva 3.0
            service = self.service_codesources
        candidates = list(service.get_installable_source(location=location))
        if len(candidates) == 1:
            return candidates[0]
        return None

    security.declareProtected(
        ViewManagementScreens, 'manage_getFileSystemLocations')
    def manage_getFileSystemLocations(self):
        service = queryUtility(ICodeSourceService)
        if service is None:
            # XXX pre-migration Silva 3.0
            service = self.service_codesources
        return map(
            lambda source: source.location,
            service.get_installable_source(identifier=self.id))

    security.declareProtected(
        ViewManagementScreens, 'manage_updateCodeSource')
    def manage_updateCodeSource(self, purge=False, REQUEST=None):
        """Update a code source from the filesystem.
        """
        installable = self._get_installable()
        if installable is None:
            if REQUEST is not None:
                return self.editCodeSource(
                    manage_tabs_message=\
                        'Could find the code source on the filesystem.')
            return False
        installable.update(self, bool(purge))
        if REQUEST is not None:
            return self.editCodeSource(
                manage_tabs_message='Source updated from the filesystem.')
        return True

    security.declareProtected(
        ViewManagementScreens, 'manage_exportCodeSource')
    def manage_exportCodeSource(self, aszip=False, REQUEST=None):
        """Export a code source to the filesystem.
        """
        installable = self._get_installable()
        if installable is None:
            if REQUEST is not None:
                return self.editCodeSource(
                    manage_tabs_message=\
                        'Could find the code source on the filesystem.')
            return None
        directory = None
        if aszip:
            directory = tempfile.mkdtemp('-codesource-export')
        installable.export(self, directory)
        if not aszip:
            if REQUEST is not None:
                return self.editCodeSource(
                    manage_tabs_message='Source exported to the filesystem.')
            return None
        result = io.BytesIO()
        archive = zipfile.ZipFile(result, 'w')
        for path, directories, filenames in os.walk(directory):
            root = path[len(directory):]
            if root:
                root = os.path.join(self.getId(), root)
            else:
                root = self.getId()
            for filename in filenames:
                archive.write(os.path.join(path, filename),
                              os.path.join(root, filename))
        archive.close()
        shutil.rmtree(directory)
        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader(
                'Content-Type',
                'application/zip')
            REQUEST.RESPONSE.setHeader(
                'Content-Disposition',
                'attachment;filename=%s.zip' % self.getId())
        return result.getvalue()

    security.declareProtected(
        ViewManagementScreens, 'manage_editCodeSource')
    def manage_editCodeSource(
        self, title, script_id, data_encoding, description=None, location=None,
        cacheable=None, previewable=None, usable=None, script_layers=None):
        """ Edit a code source settings.
        """
        msg = u''

        if location is not None and location != self._fs_location:
            if location:
                installable = self._get_installable(location)
                if installable is None:
                    msg += "Invalid location for the code source " + \
                        "definition, not changed! "
                    return self.editCodeSource(manage_tabs_message=msg)
            self._fs_location = location
            msg += "Code source location changed. "

        if data_encoding != self._data_encoding:
            try:
                unicode('abcd', data_encoding, 'replace')
            except LookupError:
                # unknown encoding, return error message
                msg += "Unknown encoding %s, not changed! " % data_encoding
                return self.editCodeSource(manage_tabs_message=msg)
            self.set_data_encoding(data_encoding)
            msg += u'Data encoding changed. '

        if script_layers is not None:
            try:
                self.set_script_layers(script_layers)
            except ValueError as error:
                msg += "Error while setting script layers: %s" % error.args[0]
                return self.editCodeSource(manage_tabs_message=msg)

        title = unicode(title, self.management_page_charset)
        if title and title != self.title:
            self.title = title
            msg += "Title changed. "

        if script_id and script_id != self._script_id:
            self._script_id = script_id
            msg += "Script id changed. "

        # Assume description is in the encoding as specified
        # by "management_page_charset". Store it in unicode.
        if description is not None:
            description = unicode(description, self.management_page_charset)
            if description != self._description:
                self.set_description(description)
                msg += "Description changed. "

        if not bool(cacheable) is self.is_cacheable():
            self.set_cacheable(bool(cacheable))
            msg += "Cacheability setting changed. "

        if not bool(usable) is self.is_usable():
            self.set_usable(bool(usable))
            msg += "Usability setting changed. "

        if not bool(previewable) is self.is_previewable():
            self.set_previewable(bool(previewable))
            msg += "Previewable setting changed. "

        return self.editCodeSource(manage_tabs_message=msg)

InitializeClass(CodeSource)


manage_addCodeSourceForm = PageTemplateFile(
    "www/codeSourceAdd", globals(),
    __name__='manage_addCodeSourceForm')


def manage_addCodeSource(
    context, id, title=None, script_id=None, fs_location=None,REQUEST=None):
    """Add a CodeSource object
    """
    cs = CodeSource(id, script_id, fs_location)
    if title is not None:
        title = unicode(title, cs.management_page_charset)
        cs.set_title(title)
    context._setObject(id, cs)
    cs = context._getOb(id)
    cs.set_form(ZMIForm('form', 'Parameters form', unicode_mode=1))

    add_and_edit(context, id, REQUEST, screen='editCodeSource')
    return ''
