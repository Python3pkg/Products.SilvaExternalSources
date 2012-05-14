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
from ZODB.broken import Broken

from Products.SilvaExternalSources.interfaces import ICodeSource
from Products.SilvaExternalSources.interfaces import ICodeSourceService
from Products.SilvaExternalSources.interfaces import ICodeSourceInstaller
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
from silva.translations import translate as _

logger = logging.getLogger('silva.externalsources')


CONFIGURATION_FILE = 'source.ini'
# All the code following are default helper to help you to install
# your code-soruces packaged on the file system.

def install_pt(context, data, id, extension):
    """Install a page template.
    """
    factory = context.manage_addProduct['PageTemplates']
    factory.manage_addPageTemplate(id, '', data.read())

def install_file(context, data, id, extension):
    """Install an Image file.
    """
    factory = context.manage_addProduct['OFSP']
    factory.manage_addImage(id, file=data)

def install_py(context, data, id, extension):
    """Install a Python script.
    """
    factory = context.manage_addProduct['PythonScripts']
    factory.manage_addPythonScript(id)
    script = getattr(context, id)
    script.write(data.read())

def install_xml(context, data, id, extension):
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



INSTALLERS = {
    '.png': install_file,
    '.gif': install_file,
    '.jpeg': install_file,
    '.jpg': install_file,
    '.pt': install_pt,
    '.py': install_py,
    '.xml': install_xml,
    '.js': install_file,
    '.css': install_file,
    '.txt': install_pt}
KEEP_EXTENSION_OF = ['.png', '.gif', '.jpg', '.jpeg', '.js', '.css']

class CodeSourceInstallable(object):
    grok.implements(ICodeSourceInstaller)

    def __init__(self, location, directory, files):
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(directory, CONFIGURATION_FILE))
        self._directory = directory
        self._files = files
        self._location = location

    def validate(self):
        """Return true if the definition is complete.
        """
        valid = True
        if not self._config.has_section('source'):
            valid = False
        elif not self._config.has_option('source', 'id'):
            valid = False
        elif not self._config.has_option('source', 'title'):
            valid = False
        elif not self._config.has_option('source', 'render_id'):
            valid = False
        if not valid:
            logger.error('invalid source definition at %s' % self._directory)
        return valid

    @CachedProperty
    def identifier(self):
        return self._config.get('source', 'id')

    @CachedProperty
    def title(self):
        return self._config.get('source', 'title')

    @CachedProperty
    def script_id(self):
        return self._config.get('source', 'render_id')

    @CachedProperty
    def description(self):
        if self._config.has_option('source', 'description'):
            return self._config.get('source', 'description')
        return None

    @property
    def location(self):
        return self._location

    def is_installed(self, folder):
        return self.identifier in folder.objectIds()

    def install(self, folder):
        if self.is_installed(folder):
            return False

        factory = folder.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource(self.identifier, fs_location=self.location)

        source = folder._getOb(self.identifier)
        return self.update(source)

    def update(self, source):
        assert ICodeSource.providedBy(source)
        assert source.get_fs_location() == self.location, u"Invalid source"
        source.set_title(self.title)
        source.set_script_id(self.script_id)
        if self.description:
            source.set_description(self.description)
        if self._config.has_option('source', 'cacheable'):
            value = self._config.getboolean('source', 'cacheable')
            source.set_cacheable(value)
        if self._config.has_option('source', 'previewable'):
            value = self._config.getboolean('source', 'previewable')
            source.set_previewable(value)
        if self._config.has_option('source', 'usable'):
            value = self._config.getboolean('source', 'usable')
            source.set_usable(value)

        for filename in self._files:
            if filename == CONFIGURATION_FILE:
                continue
            name, extension = os.path.splitext(filename)
            installer = INSTALLERS.get(extension, None)
            if installer is None:
                logger.info(
                    u"don't know how to install file %s for code source %s" % (
                        filename, self.identifier))
                continue
            if extension in KEEP_EXTENSION_OF:
                name = filename
            if name in source.objectIds():
                source.manage_delObjects([name])
            with open(os.path.join(self._directory, filename), 'rb') as data:
                installer(source, data, name, extension)

        return True


class CodeSourceService(SilvaService):
    meta_type = 'Silva Code Source Service'

    grok.implements(ICodeSourceService)
    grok.name('service_codesources')
    silvaconf.icon('www/codesource_service.png')

    security = ClassSecurityInfo()
    manage_options = (
        {'label':'Existing Code Sources',
         'action':'manage_existing_codesources'},
        {'label':'Install Code Sources',
         'action':'manage_install_codesources'},
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
                source_location = (
                    entry_point.dist.project_name + ':' +
                    source_directory[len(entry_point.dist.location):])
                sources.append(CodeSourceInstallable(
                        source_location,
                        source_directory,
                        source_files))
        return sources

    security.declareProtected(
        'View management screens', 'get_installable_source')
    def get_installable_source(self, identifier=None, location=None):
        if identifier is not None:
            test = lambda s: s.identifier == identifier
        elif location is not None:
            test = lambda s: s.location == location
        else:
            raise NotImplementedError
        sources = self.get_installable_sources()
        for source in sources:
            if test(source):
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
        self.status = None
        if find:
            self.context.find_installed_sources()
            self.status = _(u"Sources refreshed.")

        self.sources = []
        for source in self.context.get_installed_sources():
            if isinstance(source, Broken):
                self.sources.append(
                    {'id': source.getId(),
                     'problems': ['Filesystem code is missing'],
                     'title': 'Corresponding Source implementation is missing',
                     'path': '/'.join(source.getPhysicalPath()),
                     'url': None})
            else:
                self.sources.append({'id': source.getId(),
                                     'problems': source.test_source(),
                                     'title': source.get_title(),
                                     'path': '/'.join(source.getPhysicalPath()),
                                     'url': source.absolute_url()})


class ManageInstallCodeSources(silvaviews.ZMIView):
    grok.name('manage_install_codesources')

    def update(self, install=False, sources=[]):
        self.status = []
        if install:
            installed = []
            if not isinstance(sources, list):
                sources = [sources]
            for source in sources:
                installable = self.context.get_installable_source(source)
                if installable.install(self.context.get_root()):
                    installed.append(installable.title)
            if installed:
                self.status = _(u"Installed sources ${sources}.",
                                mapping=dict(sources=', '.join(installed)))
            else:
                self.status = _(u"Could not install anything.")

        self.sources = []
        for source in self.context.get_installable_sources():
            self.sources.append(source)
