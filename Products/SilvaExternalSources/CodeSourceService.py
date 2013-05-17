# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import collections
import os
import re
import logging
import ConfigParser
from datetime import datetime
from pkg_resources import iter_entry_points

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.interfaces import IObjectWillBeRemovedEvent
from ZODB.broken import Broken

from Products.Formulator.Form import ZMIForm
from Products.Formulator.FormToXML import formToXML

from five import grok
from zope.component import getUtility, queryUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectAddedEvent

from silva.core import conf as silvaconf
from silva.core.interfaces import IContainer
from silva.core.interfaces import IMimeTypeClassifier
from silva.core.services.base import SilvaService
from silva.core.services.utils import walk_silva_tree
from silva.core.views import views as silvaviews
from silva.translations import translate as _

from .interfaces import ICodeSource, ICodeSourceService, ICodeSourceInstaller
from .interfaces import ISourceErrors

logger = logging.getLogger('silva.externalsources')


CONFIGURATION_FILE = 'source.ini'
PARAMETERS_FILE = 'parameters.xml'
# All the code following are default helper to help you to install
# your code-sources packaged on the file system.


class Exporter(object):

    def __init__(self, content):
        self.content = content

    def get_filename(self, identifier):
        raise NotImplemented

    def __call__(self, filename):
        raise NotImplemented


class PageTemplateExporter(Exporter):
    """Export a page template. If the name of the template is in upper
    case this will create a .txt file, a .pt otherwise.
    """

    def get_filename(self, identifier):
        if '.' not in identifier:
            if identifier.isupper():
                return identifier + '.txt'
            else:
                return identifier + '.pt'
        return identifier

    def __call__(self, filename):
        with open(filename, 'wb') as target:
            data = self.content.read()
            if isinstance(data, unicode):
                data = data.encode('utf-8')
            if not data.endswith(os.linesep):
                data += os.linesep
            target.write(data)


class FileExporter(Exporter):
    """Export a file or an image. If identifier doesn't contains an
    extension, guess one from the filename.
    """

    def get_filename(self, identifier):
        if '.' not in identifier:
            guess_extension = getUtility(IMimeTypeClassifier).guess_extension
            return identifier + guess_extension(self.content.content_type)
        return identifier

    def __call__(self, filename):
        with open(filename, 'wb') as target:
            data = self.content.data
            if isinstance(data, basestring):
                target.write(data)
            else:
                while data is not None:
                    target.write( data.data )
                    data = data.next


class ScriptExporter(PageTemplateExporter):

    def get_filename(self, identifier):
        if '.' not in identifier:
            return identifier + '.py'
        return identifier


class Importer(object):
    keep_extension = False

    def __call__(self, context, identifier, data):
        raise NotImplemented


class PageTemplateImporter(Importer):
    """Install a page template.
    """

    def __call__(self, context, identifier, data):
        factory = context.manage_addProduct['PageTemplates']
        factory.manage_addPageTemplate(identifier, '', data.read())


class FileImporter(Importer):
    """Install a File.
    """
    keep_extension = True

    def __call__(self, context, identifier, data):
        factory = context.manage_addProduct['OFSP']
        factory.manage_addFile(identifier, file=data)


class ImageImporter(FileImporter):
    """Install an Image.
    """

    def __call__(self, context, identifier, data):
        factory = context.manage_addProduct['OFSP']
        factory.manage_addImage(identifier, file=data)


class PythonScriptImporter(Importer):
    """Install a Python script.
    """

    def __call__(self, context, identifier, data):
        factory = context.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(identifier)
        script = context._getOb(identifier)
        script.write(data.read())


class FormulatorImporter(Importer):

    def __call__(self, context, identifier, data):
        form = ZMIForm(identifier, 'Parameters form')
        try:
            form.set_xml(data.read())
            context.set_form(form)
        except:
            logger.exception(
                'Error while installing Formulator form id "%s" in "%s"' % (
                id, '/'.join(context.getPhysicalPath())))


EXPORTERS = {
    'File': FileExporter,
    'Image': FileExporter,
    'Script (Python)': ScriptExporter,
    'Page Template': PageTemplateExporter,
    }
INSTALLERS = {
    '.png':ImageImporter,
    '.gif': ImageImporter,
    '.jpeg': ImageImporter,
    '.jpg': ImageImporter,
    '.pt': PageTemplateImporter,
    '.txt': PageTemplateImporter,
    '.py': PythonScriptImporter,
    '.xml': FormulatorImporter,
    None: FileImporter,} # None is the default installer.

class CodeSourceInstallable(object):
    grok.implements(ICodeSourceInstaller)

    def __init__(self, location, directory, files):
        self._config = ConfigParser.ConfigParser()
        self._config_filename = os.path.join(directory, CONFIGURATION_FILE)
        if os.path.isfile(self._config_filename):
            self._config.read(self._config_filename)
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

    @property
    def identifier(self):
        if self._config.has_option('source', 'id'):
            return self._config.get('source', 'id')
        return os.path.basename(self._directory)

    @property
    def title(self):
        if self._config.has_option('source', 'title'):
            return self._config.get('source', 'title')
        return self.identifier

    @property
    def script_id(self):
        if self._config.has_option('source', 'render_id'):
            return self._config.get('source', 'render_id')
        return ''

    @property
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

    def _get_installables(self):
        for filename in self._files:
            if filename == CONFIGURATION_FILE:
                continue
            identifier, extension = os.path.splitext(filename)
            factory = INSTALLERS.get(extension, None)
            if factory is None:
                # Default to None, file default installer.
                factory = INSTALLERS[None]
            if factory.keep_extension:
                identifier = filename
            yield identifier, filename, factory()

    def export(self, source, directory=None):
        assert ICodeSource.providedBy(source)
        assert source.get_fs_location() == self.location, u"Invalid source"
        # Step 1, export configuration.
        if not self._config.has_section('source'):
            self._config.add_section('source')

        def set_value(key, value):
            if value:
                self._config.set('source', key, value)
            elif self._config.has_option('source', key):
                self._config.remove_option('source', key)

        set_value('id', source.getId())
        set_value('title', source.get_title())
        set_value('description', source.get_description())
        set_value('render_id', source.get_script_id())
        set_value('alternate_render_ids', source.get_script_layers())
        set_value('usuable', source.is_usable() and "yes" or "no")
        set_value('previewable', source.is_previewable() and "yes" or "no")
        set_value('cacheable', source.is_cacheable() and "yes" or "no")

        if directory is None:
            directory = self._directory

        configuration_filename = os.path.join(directory, CONFIGURATION_FILE)
        files_to_keep = [CONFIGURATION_FILE]
        with open(configuration_filename, 'wb') as config_file:
            self._config.write(config_file)

        # Step 2, export parameters if any or delete the file.
        parameters = source.get_parameters_form()
        if parameters is not None:
            parameters_filename = os.path.join(directory, PARAMETERS_FILE)
            files_to_keep.append(PARAMETERS_FILE)
            with open(parameters_filename, 'w') as parameters_file:
                parameters_file.write(formToXML(parameters) + os.linesep)

        existing_files_mapping = {}
        for identifier, filename, installer in self._get_installables():
            existing_files_mapping[identifier] = filename

        # Step 2, export files.
        for identifier, content in source.objectItems():
            factory = EXPORTERS.get(content.meta_type, None)
            if factory is None:
                logger.info(
                    u"don't know how to export %s for code source %s" % (
                        content.meta_type, self.identifier))
                continue
            exporter = factory(content)
            if identifier in existing_files_mapping:
                filename = existing_files_mapping[identifier]
            else:
                filename = exporter.get_filename(identifier)
            exporter(os.path.join(directory, filename))
            files_to_keep.append(filename)

        # Step 3, purge files that were not recreated.
        for filename in os.listdir(directory):
            if filename not in files_to_keep:
                os.unlink(os.path.join(directory, filename))
        if self._directory == directory:
            self._files = files_to_keep

    def update(self, source, purge=False):
        assert ICodeSource.providedBy(source)
        assert source.get_fs_location() == self.location, u"Invalid source"
        assert self.validate()
        source.set_title(self.title)
        source.set_script_id(self.script_id)
        if self.description:
            source.set_description(self.description)
        if self._config.has_option('source', 'alternate_render_ids'):
            value = self._config.get('source', 'alternate_render_ids')
            try:
                source.set_script_layers(value)
            except ValueError:
                pass
        if self._config.has_option('source', 'cacheable'):
            value = self._config.getboolean('source', 'cacheable')
            source.set_cacheable(value)
        if self._config.has_option('source', 'previewable'):
            value = self._config.getboolean('source', 'previewable')
            source.set_previewable(value)
        if self._config.has_option('source', 'usable'):
            value = self._config.getboolean('source', 'usable')
            source.set_usable(value)

        installed = []
        for identifier, filename, installer in self._get_installables():
            if identifier in installed:
                raise AssertionError(u"Duplicate file")
            if identifier in source.objectIds():
                source.manage_delObjects([identifier])
            with open(os.path.join(self._directory, filename), 'rb') as data:
                installer(source, identifier, data)
            installed.append(identifier)
        if purge:
            # Remove other files.
            source.manage_delObjects(
                list(set(source.objectIds()).difference(set(installed))))

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
        {'label': 'External Sources Errors',
         'action': 'manage_sources_errors'}
        ) + SilvaService.manage_options

    # This is used a marker in to be backward compatible.
    _installed_sources = None

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
        if self._installed_sources is not None:
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
    def get_installable_sources(self, refresh=False):
        if not refresh and hasattr(self.aq_base,  '_v_installable_sources'):
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
        for source in self.get_installable_sources():
            if test(source):
                yield source


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
        if service._installed_sources is None:
            service._installed_sources = []
        if source_id not in service._installed_sources:
            service._installed_sources.append(source_id)
            service._p_changed = True


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
    if service is not None and service._installed_sources is not None:
        source_id = getUtility(IIntIds).register(source)
        if source_id in service._installed_sources:
            service._installed_sources.remove(source_id)
            service._p_changed = True


OBJECT_ADDRESS = re.compile('0x([0-9a-f])*')

class SourcesError(object):
    """Describe a code source error.
    """

    def __init__(self, info, cleaned):
        self.info = info
        self._cleaned = cleaned
        self.count = 1
        self.when = datetime.now()

    def is_duplicate(self, other):
        if other == self._cleaned:
            self.count += 1
            return True
        return False

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)


class SourcesErrorsReporter(grok.GlobalUtility):
    grok.implements(ISourceErrors)
    grok.provides(ISourceErrors)

    def __init__(self):
        self.clear()

    def report(self, info):
        logger.error(info)
        cleaned = OBJECT_ADDRESS.sub('0xXXXXXXX', info)
        for error in self.__errors:
            if error.is_duplicate(cleaned):
                return
        self.__errors.append(SourcesError(info, cleaned))

    def __len__(self):
        return len(self.__errors)

    def fetch(self):
        return list(reversed(self.__errors))

    def clear(self):
        self.__errors = collections.deque([], 25)


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

    def update(self, install=False, refresh=False, locations=[]):
        self.status = []
        if install:
            notfound = []
            installed = []
            notinstalled = []
            if not isinstance(locations, list):
                locations = [locations]
            for location in locations:
                candidates = list(self.context.get_installable_source(
                        location=location))
                if len(candidates) != 1:
                    notfound.append(location)
                else:
                    installable = candidates[0]
                    if installable.install(self.context.get_root()):
                        installed.append(installable.title)
                    else:
                        notinstalled.append(installable.title)
            if installed:
                if notinstalled:
                    self.status = _(
                        u"Installed sources ${installed} but ${notinstalled} "
                        u"where already installed.",
                        mapping=dict(installed=', '.join(installed),
                                     notinstalled=', '.join(notinstalled)))
                else:
                    self.status = _(
                        u"Installed sources ${installed}.",
                        mapping=dict(installed=', '.join(installed)))
            else:
                self.status = _(
                    u"Sources ${notinstalled} are already installed.",
                    mapping=dict(notinstalled=', '.join(notinstalled)))

        self.sources = []
        for source in self.context.get_installable_sources(refresh=refresh):
            self.sources.append(source)


class ManageSourcesErrors(silvaviews.ZMIView):
    grok.name('manage_sources_errors')

    def update(self):
        errors = getUtility(ISourceErrors)
        if 'clear' in self.request.form:
            errors.clear()
        self.errors = errors.fetch()
