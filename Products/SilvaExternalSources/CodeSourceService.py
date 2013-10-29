# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import collections
import os
import re
import logging
import ConfigParser
import shutil
import pkg_resources
import operator

from datetime import datetime
from pkg_resources import iter_entry_points

from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.interfaces import IObjectWillBeRemovedEvent
from ZODB.broken import Broken

from Products.Formulator.Form import ZMIForm
from Products.Formulator.FormToXML import formToXML
from Products.Silva.ExtensionRegistry import extensionRegistry

from five import grok
from zope.interface import Interface
from zope import schema
from zope.component import getUtility, queryUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from js.jquery import jquery

from silva.core import conf as silvaconf
from silva.core.interfaces import IContainer, ISilvaConfigurableService
from silva.core.interfaces import IMimeTypeClassifier
from silva.core.messages.interfaces import IMessageService
from silva.core.services.base import SilvaService
from silva.core.services.utils import walk_silva_tree
from silva.core.views import views as silvaviews
from silva.fanstatic import need
from silva.translations import translate as _
from silva.ui import rest, menu
from zeam.form import silva as silvaforms

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

    def get_path(self, identifier):
        raise NotImplemented

    def __call__(self, path):
        raise NotImplemented


class PageTemplateExporter(Exporter):
    """Export a page template. If the name of the template is in upper
    case this will create a .txt file, a .pt otherwise.
    """

    def get_path(self, identifier):
        if '.' not in identifier:
            if identifier.isupper():
                return identifier + '.txt'
            else:
                return identifier + '.pt'
        return identifier

    def __call__(self, path):
        with open(path, 'wb') as target:
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

    def get_path(self, identifier):
        if '.' not in identifier:
            guess_extension = getUtility(IMimeTypeClassifier).guess_extension
            return identifier + guess_extension(self.content.content_type)
        return identifier

    def __call__(self, path):
        with open(path, 'wb') as target:
            data = self.content.data
            if isinstance(data, basestring):
                target.write(data)
            else:
                while data is not None:
                    target.write(data.data)
                    data = data.next


class ScriptExporter(PageTemplateExporter):

    def get_path(self, identifier):
        return identifier + '.py'


class DTMLExporter(Exporter):

    def get_path(self, identifier):
        return identifier + '.dtml'

    def __call__(self, path):
        with open(path, 'wb') as target:
            target.write(self.content.raw)


class FormulatorExporter(Exporter):

    def get_path(self, identifier):
        return identifier + '.xml'

    def __call__(self, path):
        with open(path, 'w') as target:
            target.write(formToXML(self.content))


class FolderExporter(Exporter):

    def get_path(self, identifier):
        return identifier

    def __call__(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            existing = []
        else:
            existing = os.listdir(path)
        exported = []
        for identifier, content in self.content.objectItems():
            factory = EXPORTERS.get(content.meta_type, None)
            if factory is None:
                logger.info(
                    u"don't know how to export %s for code source %s",
                    content.meta_type, self.identifier)
                continue
            exporter = factory(content)
            filename = exporter.get_path(identifier)
            try:
                exporter(os.path.join(path, filename))
            except:
                logger.error(
                    "failed to export %s for code source %s",
                    content.meta_type, self.identifier)
            exported.append(filename)
        for filename in existing:
            if filename not in exported:
                fullname = os.path.join(path, filename)
                if os.path.isdir(fullname):
                    shutil.rmtree(fullname)
                else:
                    os.unlink(fullname)


class ExternalMethodExporter(Exporter):

    def get_path(self, identifier):
        return identifier + ".em"

    def __call__(self, path):
        with open(path, 'wb') as target:
            target.write('title:string=%s\n' % self.content.title)
            target.write('module:string=%s\n' % self.content._module)
            target.write('function:string=%s\n' % self.content._function)


class Importer(object):
    keep_extension = False

    def __call__(self, context, identifier, path):
        raise NotImplemented


class PageTemplateImporter(Importer):
    """Install a page template.
    """

    def __call__(self, context, identifier, path):
        with open(path, 'rb') as data:
            factory = context.manage_addProduct['PageTemplates']
            factory.manage_addPageTemplate(identifier, '', data.read())


class FileImporter(Importer):
    """Install a File.
    """
    keep_extension = True

    def __call__(self, context, identifier, path):
        with open(path, 'rb') as data:
            factory = context.manage_addProduct['OFSP']
            factory.manage_addFile(identifier, file=data)


class ImageImporter(FileImporter):
    """Install an Image.
    """

    def __call__(self, context, identifier, path):
        with open(path, 'rb') as data:
            factory = context.manage_addProduct['OFSP']
            factory.manage_addImage(identifier, file=data)


class PythonScriptImporter(Importer):
    """Install a Python script.
    """

    def __call__(self, context, identifier, path):
        with open(path, 'rb') as data:
            factory = context.manage_addProduct['PythonScripts']
            factory.manage_addPythonScript(identifier)
            script = context._getOb(identifier)
            script.write(data.read())


class DTMLImporter(Importer):

    def __call__(self, context, identifier, path):
        with open(path, 'rb') as data:
            factory = context.manage_addProduct['OFS']
            factory.manage_addDTMLDocument(identifier)
            dtml = context._getOb(identifier)
            dtml.munge(data.read())


class FormulatorImporter(Importer):

    def __call__(self, context, identifier, path):
        with open(path, 'rb') as data:
            form = ZMIForm(identifier, 'Parameters form')
            try:
                form.set_xml(data.read())
            except:
                logger.exception('''
                    Error while installing Formulator form id "%s" in "%s"
                    ''' % (identifier, '/'.join(context.getPhysicalPath())))
            else:
                if identifier == 'parameters':
                    context.set_form(form)
                else:
                    context._setObject(identifier, form)


class FolderOrFileImporter(Importer):
    keep_extension = True

    def __call__(self, context, identifier, path):
        factory = context.manage_addProduct['OFSP']
        if os.path.isdir(path):
            factory.manage_addFolder(identifier)
            container = context._getOb(identifier)
            for filename in os.listdir(path):
                if filename.startswith('.'):
                    continue
                identifier, extension = os.path.splitext(filename)
                factory = INSTALLERS.get(extension, None)
                if factory is None:
                    # Default to None, file default installer.
                    factory = INSTALLERS[None]
                if factory.keep_extension:
                    identifier = filename
                installer = factory()
                if identifier in container.objectIds():
                    container.manage_delObjects([identifier])
                installer(container, identifier,
                          os.path.join(path, filename))
        else:
            with open(path, 'rb') as data:
                factory.manage_addFile(identifier, file=data)


EXPORTERS = {
    'File': FileExporter,
    'Image': FileExporter,
    'Script (Python)': ScriptExporter,
    'Page Template': PageTemplateExporter,
    'Folder': FolderExporter,
    'DTML Document': DTMLExporter,
    'DTML Method': DTMLExporter,
    'External Method': ExternalMethodExporter,
    'Formulator Form': FormulatorExporter,
    }
INSTALLERS = {
    '.png': ImageImporter,
    '.gif': ImageImporter,
    '.jpeg': ImageImporter,
    '.jpg': ImageImporter,
    '.pt': PageTemplateImporter,
    '.txt': PageTemplateImporter,
    '.py': PythonScriptImporter,
    '.xml': FormulatorImporter,
    '.dtml': DTMLImporter,
    None: FolderOrFileImporter, }  # None is the default installer.


class CodeSourceInstallable(object):
    grok.implements(ICodeSourceInstaller)

    def __init__(self, location, directory, extension=None):
        self._config = ConfigParser.ConfigParser()
        self._config_filename = os.path.join(directory, CONFIGURATION_FILE)
        if os.path.isfile(self._config_filename):
            self._config.read(self._config_filename)
        self._directory = directory
        self._location = location
        self.extension = extension

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
        source = getattr(folder, self.identifier, None)
        return (ICodeSource.providedBy(source) and
                source.get_fs_location() == self._location)

    def install(self, folder):
        if self.is_installed(folder):
            return False

        factory = folder.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource(self.identifier,
                                     fs_location=self.location)

        source = folder._getOb(self.identifier)
        return self.update(source)

    def _get_installables(self):
        if not os.path.isdir(self._directory):
            return
        for filename in os.listdir(self._directory):
            if filename == CONFIGURATION_FILE or filename.startswith('.'):
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
        if directory is None:
            assert source.get_fs_location() == self.location, u"Invalid source"
            directory = self._directory

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
                try:
                    parameters_file.write(formToXML(parameters) + os.linesep)
                except:
                    logger.error(
                        "failed to export parameters for code source %s",
                        self.identifier)

        existing_mapping = {}
        for identifier, filename, installer in self._get_installables():
            existing_mapping[identifier] = filename

        # Step 2, export files.
        for identifier, content in source.objectItems():
            factory = EXPORTERS.get(content.meta_type, None)
            if factory is None:
                logger.info(
                    u"don't know how to export %s for code source %s",
                    content.meta_type, self.identifier)
                continue
            exporter = factory(content)
            if identifier in existing_mapping:
                filename = existing_mapping[identifier]
            else:
                filename = exporter.get_path(identifier)
            try:
                exporter(os.path.join(directory, filename))
            except:
                logger.error(
                    "failed to export %s for code source %s",
                    content.meta_type, self.identifier)
            files_to_keep.append(filename)

        # Step 3, purge files that were not recreated.
        for filename in os.listdir(directory):
            if filename not in files_to_keep:
                fullname = os.path.join(directory, filename)
                if os.path.isdir(fullname):
                    shutil.rmtree(fullname)
                else:
                    os.unlink(fullname)
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
            installer(source, identifier,
                      os.path.join(self._directory, filename))
            installed.append(identifier)
        if purge:
            # Remove other files.
            source.manage_delObjects(
                list(set(source.objectIds()).difference(set(installed))))

        return True


class CodeSourceService(SilvaService):
    meta_type = 'Silva Code Source Service'

    grok.implements(ICodeSourceService, ISilvaConfigurableService)
    grok.name('service_codesources')
    silvaconf.icon('www/codesource_service.png')

    security = ClassSecurityInfo()
    manage_options = (
        {'label': 'Available Code Sources',
         'action': 'manage_existing_codesources'},
        {'label': 'Install Code Sources',
         'action': 'manage_install_codesources'},
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
        for source in walk_silva_tree(self.get_root(), requires=ICodeSource):
            self._installed_sources.append(service.register(source))

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
        for entry_point in iter_entry_points(
                'Products.SilvaExternalSources.sources'):
            module = entry_point.load()
            directory = os.path.dirname(module.__file__)
            for source_identifier in os.listdir(directory):
                source_directory = os.path.join(directory, source_identifier)
                if not os.path.isdir(source_directory):
                    continue
                source_files = os.listdir(source_directory)
                if CONFIGURATION_FILE not in source_files:
                    continue
                source_location = (
                    entry_point.dist.project_name + ':' +
                    source_directory[len(entry_point.dist.location):])
                sources.append(CodeSourceInstallable(
                    source_location,
                    source_directory,
                    extension=entry_point.dist.project_name))
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


class ExistingCodeSourcesMixin(object):

    def update(self, find=False, below=None, child=False,
               update=False, bind=False, sources=None):
        self.status = None
        if find:
            self.context.find_installed_sources()
            self.status = _(u"Sources refreshed.")

        self.sources = []
        self.include_child = bool(child)
        if below:
            below = below.strip()
            if not below.endswith('/'):
                below += '/'
        for source in self.context.get_installed_sources():
            path = '/'.join(source.getPhysicalPath())
            if (below and (not path.startswith(below) or
                           (not child and '/' in path[len(below):]))):
                continue
            if isinstance(source, Broken):
                self.sources.append(
                    {'id': source.getId(),
                     'problems': [_(u'Filesystem code is missing')],
                     'title': _(u'Corresponding Source implementation is missing'),
                     'path': path,
                     'url': None})
                continue
            message = None
            if ICodeSource.providedBy(source):
                if update and (sources is None or source.getId() in sources):
                    installable = source._get_installable()
                    if (installable is not None and
                            os.path.isdir(installable._directory)):
                        installable.update(source, True)
                        message = _('Source updated.')
                    else:
                        self.sources.append(
                            {'id': source.getId(),
                             'problems': [_(u'Filesystem code have been deleted')],
                             'title': source.get_title(),
                             'path':  path,
                             'message': None,
                             'url': source.absolute_url()})
                        continue
                elif bind and not source.get_fs_location():
                    candidates = source.manage_getFileSystemLocations()
                    if len(candidates) == 1:
                        source._fs_location = candidates[0]
                        message = _('Source associated with ${location}.',
                                    mapping=dict(location=candidates[0]))
            self.sources.append({'id': source.getId(),
                                 'problems': source.test_source(),
                                 'title': source.get_title(),
                                 'path': path,
                                 'url': source.absolute_url(),
                                 'message': message})
        if below:
            self.filter = below.rstrip('/')
        else:
            self.filter = '/'.join(aq_parent(self.context).getPhysicalPath())


class ManageExistingCodeSources(ExistingCodeSourcesMixin, silvaviews.ZMIView):
    grok.name('manage_existing_codesources')
    grok.context(CodeSourceService)


class ConfigureExisting(ExistingCodeSourcesMixin, rest.PageWithTemplateREST):
    grok.adapts(rest.Screen, CodeSourceService)
    grok.name('admin-existing')
    grok.require('zope2.ViewManagementScreens')

    def get_menu_title(self):
        return _('Available code sources')

    def update(self):
        sources = self.request.form.get('sources')
        if sources is not None and not isinstance(sources, list):
            sources = [sources]
        super(ConfigureExisting, self).update(
            find='find' in self.request.form,
            update='update' in self.request.form,
            sources=sources)
        if self.status:
            service = getUtility(IMessageService)
            service.send(self.status, self.request, namespace='feedback')


class ConfigureExistingMenu(menu.MenuItem):
    grok.adapts(menu.ContentMenu, CodeSourceService)
    grok.order(10)
    name = _('Available')
    screen = ConfigureExisting


class InstallCodeSourcesMixin(object):
    only_uninstalled = False

    def update(self, install=False, refresh=False, locations=[]):
        self.status = None
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

        self.extensions = []
        self.sources = 0
        extensions = {}
        for source in self.context.get_installable_sources(refresh=refresh):
            if self.only_uninstalled and source.is_installed(self.context):
                continue
            sources = extensions.setdefault(source.extension, [])
            sources.append(source)
            self.sources += 1
        for name, sources in extensions.items():
            if name is None:
                self.extensions.append({
                    'title': _('Default code sources'),
                    'id': '0',
                    'description': '',
                    'sources': sources
                })
                continue
            identifier = str(name).encode('base64').strip().rstrip('=')
            extension = extensionRegistry.get_extension(name)
            if extension is None:
                self.extensions.append({
                    'title': name,
                    'id': identifier,
                    'description': '',
                    'sources': sources
                })
                continue
            self.extensions.append({
                'title': extension.title,
                'id': identifier,
                'description': extension.description,
                'sources': sources,
            })
        self.extensions.sort(key=operator.itemgetter('title'))


class ManageInstallCodeSources(InstallCodeSourcesMixin, silvaviews.ZMIView):
    grok.name('manage_install_codesources')
    grok.context(CodeSourceService)

    def update(self, install=False, refresh=False, locations=[]):
        super(ManageInstallCodeSources, self).update(
            install=install, refresh=refresh, locations=locations)
        need(jquery)


class ConfigureInstall(InstallCodeSourcesMixin, rest.PageWithTemplateREST):
    grok.adapts(rest.Screen, CodeSourceService)
    grok.name('admin')
    grok.require('zope2.ViewManagementScreens')

    only_uninstalled = True

    def get_menu_title(self):
        return _('Install code sources')

    def update(self, install=False, refresh=False, locations=[]):
        super(ConfigureInstall, self).update(
            install='install' in self.request.form,
            refresh='refresh' in self.request.form,
            locations=self.request.form.get('locations', []))
        if self.status:
            service = getUtility(IMessageService)
            service.send(self.status, self.request, namespace='feedback')


class ConfigureInstallMenu(menu.MenuItem):
    grok.adapts(menu.ContentMenu, CodeSourceService)
    grok.order(15)
    name = _('Install')
    screen = ConfigureInstall


class ManageSourcesErrors(silvaviews.ZMIView):
    grok.name('manage_sources_errors')
    grok.context(CodeSourceService)

    def update(self):
        errors = getUtility(ISourceErrors)
        if 'clear' in self.request.form:
            errors.clear()
        self.errors = errors.fetch()


def check_extension(name):
    if ':' in name:
        name, _ = name.split(':', 1)
    return name in pkg_resources.working_set.by_key


class IExportCodeSourcesFields(Interface):

    extension_name = schema.TextLine(
        title=u'Extension name',
        description=_(
            u"Enter the extension name and the entry point name, seperated by "
            u"a :. The entry point name defaults to defaults if it is not "
            u"specified."),
        constraint=check_extension,
        required=True)
    recursive = schema.Bool(
        title=u'Recursive export ?',
        default=False,
        required=False)


class ManageExportCodeSources(silvaforms.ZMIForm):
    grok.name('manage_export_codesources')
    grok.context(IContainer)

    label = u'Mass export of codesources'
    description = u'Export every codesources located in this container and ' \
        u'optionally in sub-containers.'
    fields = silvaforms.Fields(IExportCodeSourcesFields)

    @silvaforms.action('Export')
    def export(self):
        values, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        exported = []
        extension_name = values['extension_name']
        if ':' in extension_name:
            extension_name, entry_name = extension_name.split(':', 1)
        extension = pkg_resources.working_set.by_key[extension_name]
        directory = os.path.dirname(extension.load_entry_point(
            'Products.SilvaExternalSources.sources', entry_name).__file__)

        if values['recursive']:
            sources = walk_silva_tree(self.context, requires=ICodeSource)
        else:
            sources = self.context.objectValues('Silva Code Source')

        for source in sources:
            if source.meta_type != 'Silva Code Source':
                continue
            identifier = source.getId()
            target = os.path.join(directory, identifier)
            location = (
                extension.project_name + ':' +
                target[len(extension.location):])

            if source.get_fs_location() not in (None, location):
                continue
            if not os.path.exists(target):
                os.makedirs(target)
            source._fs_location = location
            installable = CodeSourceInstallable(location, target)
            installable.export(source)
            exported.append(location)
        if exported:
            self.status = 'Exported: {0}.'.format(', '.join(exported))
        else:
            self.status = 'Nothing exported.'
        return silvaforms.SUCCESS
