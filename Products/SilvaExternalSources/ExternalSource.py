# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from zope.interface import implements

# Zope
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from App.class_init import InitializeClass
import Acquisition

# Silva
from Products.Silva import SilvaPermissions as permissions
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.interfaces import IEditableExternalSource

from silva.core.interfaces import IRoot


module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.ExternalSource')


module_security.declarePublic('availableSources')
def availableSources(context):
    """List available sources in the site starting at context.
    """
    sources = {}
    while context is not None:
        for item in context.objectValues():
            if IExternalSource.providedBy(item) and item.id not in sources:
                sources[item.id] = item
        if IRoot.providedBy(context):
            break
        context = Acquisition.aq_parent(context)
    return sequence.sort(sources.items(), (('title', 'nocase', 'asc'),))


module_security.declarePublic('getSourceForId')
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
    implements(IExternalSource)
    security = ClassSecurityInfo()

    # XXX was management_page_charset = Converters.default_encoding
    # that doesn't work, because the add screens DON'T USE THE ZOPE
    # DEFAULT ENCODING! AAAAAAARGH

    management_page_charset = 'UTF-8'

    # Cannot make it 'private'; the form won't work in the ZMI if it was.
    parameters = None

    _data_encoding = 'UTF-8'
    _description = ''
    _is_cacheable = False
    _is_previewable = True

    # ACCESSORS

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_parameters_form')
    def get_parameters_form(self):
        """ get to the parameters form
        """
        return self.parameters

    security.declareProtected(
        permissions.AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """
        raise NotImplementedError

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
        return self.title


InitializeClass(ExternalSource)


class EditableExternalSource(ExternalSource):
    implements(IEditableExternalSource)
    security = ClassSecurityInfo()

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_form')
    def set_form(self, form):
        """ Set Formulator parameters form
        """
        self.parameters = form

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        """ set encoding of data
        """
        self._data_encoding = encoding

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_description')
    def set_description(self, description):
        """ set description of external source's use
        """
        self._description = description

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_cacheable')
    def set_cacheable(self, cacheable):
        """ set cacheablility of source
        """
        self._is_cacheable = cacheable

    security.declareProtected(permissions.ViewManagementScreens, 'set_previewable')
    def set_previewable(self, previewable):
        """ set previewablility (in kupu) of source
        """
        self._is_previewable = not not previewable


InitializeClass(EditableExternalSource)
