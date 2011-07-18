# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
import logging
import ConfigParser
from pkg_resources import iter_entry_points

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.interfaces import IObjectWillBeRemovedEvent


from Products.SilvaExternalSources.interfaces import ICodeSource
from Products.SilvaExternalSources.interfaces import ICodeSourceService
from Products.Formulator.Form import ZMIForm

from zope.component import getUtility, queryUtility
from zope.intid.interfaces import IIntIds
from zope.cachedescriptors.property import CachedProperty
from zope.lifecycleevent.interfaces import IObjectAddedEvent

from five import grok
from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf
from silva.core.interfaces import IContainer
from silva.core.views import views as silvaviews
from silva.core.services.utils import walk_silva_tree

logger = logging.getLogger('silva.externalsources')


CONFIGURATION_FILE = 'source.ini'
# All the code following are default helper to help you to install
# your code-soruces packaged on the file system.

def install_pt(context, data, id):
    """Install a page template.
    """
    factory = context.manage_addProduct['PageTemplates']
    factory.manage_addPageTemplate(id, '', data.read())


def install_py(context, data, id):
    """Install a Python script.
    """
    factory = context.manage_addProduct['PythonScripts']
    factory.manage_addPythonScript(id)
    script = getattr(context, id)
    script.write(data.read())


def install_xml(context, data, id):
    """Install an XML file.
    """
    form = ZMIForm('form', 'Parameters form')
    try:
        form.set_xml(data.read())
        context.set_form(form)
    except:
        logger.exception(
            'Error while installing Formulator form id "%s" in "%s"' % (
                id, '/'.join(context.getPhysicalPath())))


def install_js(context, data, id):
    """Install a JS script as a dtml file.
    """
    factory = context.manage_addProduct['OFSP']
    factory.manage_addDTMLMethod(id + '.js', '', data.read())


INSTALLERS = {
    '.pt': install_pt,
    '.py': install_py,
    '.xml': install_xml,
    '.js': install_js,
    '.txt': install_pt}


class CodeSourceInstallable(object):

    def __init__(self, directory, files):
        self.__config = ConfigParser.ConfigParser()
        self.__config.read(os.path.join(directory, CONFIGURATION_FILE))
        self.__directory = directory
        self.__files = files

    def validate(self):
        """Return true if the definition is complete.
        """
        valid = True
        if not self.__config.has_section('source'):
            valid = False
        elif not self.__config.has_option('source', 'id'):
            valid = False
        elif not self.__config.has_option('source', 'title'):
            valid = False
        elif not self.__config.has_option('source', 'render_id'):
            valid = False
        if not valid:
            logger.error('invalid source definition at %s' % self.__directory)
        return valid

    @CachedProperty
    def identifier(self):
        return self.__config.get('source', 'id')

    @CachedProperty
    def title(self):
        return self.__config.get('source', 'title')

    @CachedProperty
    def description(self):
        if self.__config.has_option('source', 'description'):
            return self.__config.get('source', 'description')
        return None

    def is_installed(self, folder):
        return self.identifier in folder.objectIds()

    def install(self, folder):
        if self.is_installed(folder):
            return False

        render_id = self.__config.get('source', 'render_id')
        factory = folder.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource(self.identifier, self.title, render_id)

        source = folder._getOb(self.identifier)
        if self.description:
            source.set_description(self.description)
        if self.__config.has_option('source', 'cacheable'):
            source.set_cacheable(self.__config.getboolean('source', 'cacheable'))
        if self.__config.has_option('source', 'previewable'):
            source.set_previewable(self.__config.getboolean('source', 'previewable'))

        for filename in self.__files:
            if filename == CONFIGURATION_FILE:
                continue
            name, extension = os.path.splitext(filename)
            installer = INSTALLERS.get(extension, None)
            if installer is None:
                logger.info(
                    u"don't know how to install file %s for code source %s" % (
                        filename, self.identifier))
                continue
            with open(os.path.join(self.__directory, filename), 'rb') as data:
                installer(source, data, name)

        return True


class CodeSourceService(SilvaService):
    meta_type = 'Silva Code Source Service'

    grok.implements(ICodeSourceService)
    grok.name('service_codesources')
    silvaconf.icon('www/codesource_service.png')

    security = ClassSecurityInfo()
    manage_options = (
        {'label':'Existing Code Sources', 'action':'manage_existing_codesources'},
        {'label':'Install Code Sources', 'action':'manage_install_codesources'},
        ) + SilvaService.manage_options

    _installed_sources = []

    security.declareProtected(
        'View management screens', 'find_installed_sources')
    def find_installed_sources(self):
        logger.info('search for code sources')
        self.clear_installed_sources()
        service = getUtility(IIntIds)
        for container in walk_silva_tree(self.get_root(), requires=IContainer):
            for content in container.objectValues():
                if ICodeSource.providedBy(content):
                    self._installed_sources.append(service.register(content))

    security.declareProtected(
        'Access contents information', 'get_installed_sources')
    def get_installed_sources(self):
        resolve = getUtility(IIntIds).getObject
        for source_id in self._installed_sources:
            try:
                yield resolve(source_id)
            except KeyError:
                pass

    security.declareProtected(
        'View management screens', 'clear_installed_sources')
    def clear_installed_sources(self):
        self._installed_sources = []

    security.declareProtected(
        'View management screens', 'get_installable_sources')
    def get_installable_sources(self):
        if hasattr(self.aq_base,  '_v_installable_sources'):
            return self._v_installable_sources
        self._v_installable_sources = sources = []
        for entry_point  in iter_entry_points(
            'Products.SilvaExternalSources.sources'):
            module = entry_point.load()
            directory = os.path.dirname(module.__file__)
            for source_directory, _, source_files in os.walk(directory):
                if source_directory == directory:
                    continue
                if CONFIGURATION_FILE not in source_files:
                    continue
                sources.append(CodeSourceInstallable(
                        source_directory, source_files))
        return sources

    security.declareProtected(
        'View management screens', 'get_installable_source')
    def get_installable_source(self, identifier):
        sources = self.get_installable_sources()
        for source in sources:
            if identifier == source.identifier:
                return source
        return None


InitializeClass(CodeSourceService)


@grok.subscribe(ICodeSource, IObjectAddedEvent)
def register_source(source, event):
    """Register newly created source to the service.
    """
    if (event.object is source and
        not IContainer.providedBy(event.newParent)):
        # The source is not added in a Silva Container so it won't be usable.
        return
    service = queryUtility(ICodeSourceService)
    if service is not None:
        source_id = getUtility(IIntIds).register(source)
        if source_id not in service._installed_sources:
            service._installed_sources.append(source_id)


@grok.subscribe(ICodeSource, IObjectWillBeRemovedEvent)
def unregister_source(source, event):
    """Remove deleted sources from the service.
    """
    if (event.object is source and
        event.newName is not None and
        IContainer.providedBy(event.newParent)):
        # We are just moving or renaming the source
        return
    service = queryUtility(ICodeSourceService)
    if service is not None:
        source_id = getUtility(IIntIds).register(source)
        if source_id in service._installed_sources:
            service._installed_sources.remove(source_id)


class ManageExistingCodeSources(silvaviews.ZMIView):
    grok.name('manage_existing_codesources')

    def update(self, find=False):
        if find:
            self.context.find_installed_sources()

        self.sources = []
        for source in self.context.get_installed_sources():
            self.sources.append({'id': source.getId(),
                                 'problems': source.test_source(),
                                 'title': source.get_title(),
                                 'path': '/'.join(source.getPhysicalPath()),
                                 'url': source.absolute_url()})


class ManageInstallCodeSources(silvaviews.ZMIView):
    grok.name('manage_install_codesources')

    def update(self, install=False, sources=[]):
        if install:
            if not isinstance(sources, list):
                sources = [sources]
            for source in sources:
                installable = self.context.get_installable_source(source)
                installable.install(self.context.get_root())

        self.sources = []
        for source in self.context.get_installable_sources():
            self.sources.append(source)
