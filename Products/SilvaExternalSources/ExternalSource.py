# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import sys
import uuid

from five import grok
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotatable, IAnnotations
import persistent

# Zope
from AccessControl import ClassSecurityInfo
from AccessControl.security import checkPermission
from App.class_init import InitializeClass
from zExceptions.ExceptionFormatter import format_exception
import Acquisition

# Silva
from Products.Silva import SilvaPermissions as permissions

from silva.translations import translate as _
from zeam.component import component
from zeam.form import silva as silvaforms
from zeam.form.ztk.widgets import TextField

from . import errors as error
from .interfaces import IExternalSource, IEditableExternalSource
from .interfaces import IExternalSourceController
from .interfaces import IExternalSourceManager, IExternalSourceInstance
from .interfaces import ISourceErrors
from .interfaces import availableSources # BB

logger = logging.getLogger('silva.externalsources')
SETTINGS_PERMISSION = 'silva.ManageSilvaContentSettings'

# BBB
def getSourceForId(context, identifier):
    """ Look for an Source with given id. Mimic normal aqcuisition,
    but skip objects which have given id but do not implement the
    ExternalSource interface.
    """
    nearest = getattr(context, identifier, None)
    if IExternalSource.providedBy(nearest):
        return nearest
    return None


class ExternalSource(Acquisition.Implicit):
    grok.implements(IExternalSource)
    security = ClassSecurityInfo()
    parameters = None

    _data_encoding = 'UTF-8'
    _description = ''
    _is_cacheable = False
    _is_previewable = True
    _is_usable = True

    # ACCESSORS

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_parameters_form')
    def get_parameters_form(self):
        """ Return the parameters fields.
        """
        return self.parameters

    security.declareProtected(
        permissions.AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """
        raise NotImplementedError

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_usable')
    def is_usable(self):
        """ Return true if the external source must be usable.
        """
        return self._is_usable

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_cacheable')
    def is_cacheable(self, **parameters):
        """ Specify the cacheability.
        """
        return self._is_cacheable

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_previewable')
    def is_previewable(self, **parameters):
        """ Specify the previewability (in kupu) of the source
        """
        if not hasattr(self, '_is_previewable'):
            self._is_previewable = True
        return self._is_previewable

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_data_encoding')
    def get_data_encoding(self):
        """ Specify the encoding of source's data.
        """
        return self._data_encoding

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_description')
    def get_description(self):
        """ Specify the use of this source.
        """
        return self._description

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_title')
    def get_title (self):
        return self.title or self.getId()

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_icon')
    def get_icon(self):
        return None


InitializeClass(ExternalSource)


class EditableExternalSource(ExternalSource):
    grok.implements(IEditableExternalSource)
    security = ClassSecurityInfo()

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_form')
    def set_form(self, form):
        """Set Formulator parameters form
        """
        self.parameters = form

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        """Set encoding of data.
        """
        self._data_encoding = encoding

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_title')
    def set_title(self, title):
        """Set title
        """
        self.title = title

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_description')
    def set_description(self, description):
        """Set description of external source's use.
        """
        self._description = description

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_cacheable')
    def set_cacheable(self, cacheable):
        """Set cacheablility of source.
        """
        self._is_cacheable = cacheable

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_previewable')
    def set_previewable(self, previewable):
        """Set previewablility of source.
        """
        self._is_previewable = bool(previewable)

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_usable')
    def set_usable(self, usable):
        """Set usability.
        """
        self._is_usable = bool(usable)

InitializeClass(EditableExternalSource)


class ExternalSourceParameters(persistent.Persistent):
    grok.implements(IExternalSourceInstance)

    __source_template = None

    def __init__(self, parameter_identifier, source_identifier):
        self.__source_identifier = source_identifier
        self.__parameter_identifier = parameter_identifier

    def get_parameter_identifier(self):
        return self.__parameter_identifier

    def get_source_identifier(self):
        return self.__source_identifier

    def get_source_template(self):
        # A source template is an HTML chunk that can be used to warp
        # around the result of an external source.
        return self.__source_template

    def set_source_template(self, template):
        self.__source_template = template


@component(IAnnotatable, provides=IExternalSourceManager)
class ExternalSourceManager(object):
    grok.implements(IExternalSourceManager)
    KEY = 'Products.SilvaExternalSources'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
        self.sources = self.annotations.get(self.KEY)

    def editable_sources(self):
        # Add the annotations if missing, and return the sources.
        # This is not done in the __init__ because it can be built
        # during tranversing (read-only).
        if self.sources is None:
            self.sources = self.annotations[self.KEY] = \
                persistent.mapping.PersistentMapping()
        return self.sources

    def new(self, source):
        assert IExternalSource.providedBy(source)
        identifier = str(uuid.uuid1())
        parameters = ExternalSourceParameters(identifier, source.id)
        self.editable_sources()[identifier] = parameters
        return parameters

    def remove(self, identifier):
        del self.editable_sources()[identifier]

    def all(self):
        if self.sources is not None:
            return set(self.sources.keys())
        return []

    def get_parameters(self, instance=None, name=None):
        parameters = None
        if instance is not None:
            if self.sources is not None:
                parameters = self.sources.get(instance)
            if parameters is None:
                raise error.ParametersMissingError(instance)
            name = parameters.get_source_identifier()
        if name is None:
            raise error.SourceMissingError('unknow')
        source = getattr(self.context, name, None)
        if source is not None and IExternalSource.providedBy(source):
            return parameters, source
        if parameters is not None:
            # XXX Return a stub here not to loose source name.
            return parameters, None
        raise error.SourceMissingError(name)

    def __call__(self, request, instance=None, name=None):
        parameters, source = self.get_parameters(instance=instance, name=name)
        return ExternalSourceController(source, self, request, parameters)


class InvalidSourceTemplate(ValueError):

    def doc(self):
        return _(u'The source template marker <!-- source output --> '
                 u'is missing.')


def validateSourceTemplate(value):
    if '<!-- source output -->' not in value:
        raise InvalidSourceTemplate()
    return True


class ExternalSourceController(silvaforms.FormData):
    grok.implements(IExternalSourceController)
    security = ClassSecurityInfo()

    actions = silvaforms.Actions()
    parameterFields = silvaforms.Fields()
    settingFields = silvaforms.Fields()
    ignoreRequest = True
    ignoreContent = False

    def __init__(self, source, manager, request, instance):
        dataManager = [
            (None,
             lambda content: silvaforms.FieldValueDataManager(self, content))]
        self.manager = manager
        self.source = source
        self.__parent__ = manager.context # Enable security checks.
        if source is not None:
            fields = source.get_parameters_form()
            if fields is not None:
                self.parameterFields = silvaforms.Fields(fields)
            if checkPermission(SETTINGS_PERMISSION, manager.context):
                self.settingFields += TextField(
                    identifier="source_template",
                    title="Source template",
                    constrainValue=validateSourceTemplate,
                    required=False)
                dataManager.append(
                    ('source_template', silvaforms.SilvaDataManager))
        self.dataManager = silvaforms.MultiDataManagerFactory(dataManager)
        super(ExternalSourceController, self).__init__(
            manager.context, request, instance)

    def getId(self):
        content = self.getContent()
        if content is not None:
            return content.get_parameter_identifier()
        return None

    security.declareProtected(
        permissions.AccessContentsInformation, 'getSourceId')
    def getSourceId(self):
        return self.source.id

    def extractData(self, fields=None):
        if fields is None:
            fields = self.parameterFields + self.settingFields
        return super(ExternalSourceController, self).extractData(fields)

    def editable(self):
        return len(self.parameterFields) != 0

    @property
    def label(self):
        if self.source is not None:
            return self.source.get_title()
        return _(u"Broken source")

    @property
    def description(self):
        if self.source is not None:
            return self.source.get_description()
        return u''

    @property
    def fields(self):
        return self.parameterFields

    def indexes(self):
        # Return index entries for Silva Indexer.
        return []

    def fulltext(self):
        # Return fulltext for the catalog
        return []

    def new(self):
        assert self.source is not None, u'Cannot create broken source'
        assert self.getContent() is None, u'Cannot override existing source'
        self.setContentData(self.manager.new(self.source))
        return self.getId()

    def copy(self, destination):
        assert self.source is not None, u'Cannot copy broken source'
        assert self.getSourceId() == destination.getSourceId()
        source = self.getContentData()
        target = destination.getContentData()
        for field in self.parameterFields:
            try:
                target.set(field.identifier, source.get(field.identifier))
            except KeyError:
                pass

    @silvaforms.action(_(u"Create"))
    def create(self):
        self.new()
        return self.save()

    @silvaforms.action(_(u"Save"))
    def save(self):
        assert self.getContent() is not None, u'Cannot save to missing source'
        if self.source is None:
            raise error.SourceMissingError('unknow')
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        manager = self.getContentData()
        for field in self.parameterFields + self.settingFields:
            value = data.getWithDefault(field.identifier)
            if value is not silvaforms.NO_CHANGE:
                manager.set(field.identifier, value)
        return silvaforms.SUCCESS

    @silvaforms.action(_(u"Remove"))
    def remove(self):
        assert self.getContent() is not None, u'Cannot remove missing source'
        manager = self.getContentData()
        identifier = self.getId()
        for field in self.parameterFields:
            manager.delete(field.identifier)
        self.manager.remove(identifier)
        return silvaforms.SUCCESS

    def fieldWidgets(self, ignoreRequest=False, ignoreContent=True, display=False):
        if display:
            self.mode = silvaforms.DISPLAY
            self.ignoreRequest = True
            self.ignoreContent = False
        else:
            self.mode = silvaforms.INPUT
            self.ignoreRequest = ignoreRequest
            self.ignoreContent = ignoreContent
        widgets = silvaforms.Widgets(form=self, request=self.request)
        widgets.extend(self.parameterFields)
        if self.settingFields and not display:
            widgets.extend(self.settingFields)
        widgets.update()
        return widgets

    security.declareProtected(
        permissions.AccessContentsInformation, 'render')
    def render(self, view=False, preview=False):
        if self.source is None:
            raise error.SourceMissingError('unknow')
        if preview and not self.source.is_previewable():
            raise error.SourcePreviewError(self)
        values = {}
        template = None
        if self.parameterFields:
            if not self.ignoreRequest:
                values, errors = self.extractData(self.parameterFields)
                if errors:
                    raise error.ParametersError(errors)
            elif not self.ignoreContent and self.getContent() is not None :
                template = self.getContent().get_source_template()
                manager = self.getContentData()
                for field in self.parameterFields:
                    try:
                        value = manager.get(field.identifier)
                    except KeyError:
                        value = field.getDefaultValue(self)
                    values[field.identifier] = value
            else:
                raise error.ParametersError()

        try:
            html = self.source.to_html(self.context, self.request, **values)
        except:
            info = u''.join(format_exception(*sys.exc_info()))
            getUtility(ISourceErrors).report(info)
            raise error.SourceRenderingError(self, info)
        if template:
            html = template.replace('<!-- source output -->', html)
        return html

InitializeClass(ExternalSourceController)
