# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""Install for Silva External Sources extension
"""
# Python
from warnings import warn
import logging
import os

# Zope
from App.Common import package_home
from Products.Formulator.Form import ZMIForm
from zExceptions import BadRequest

# Silva
from Products.Silva.install import add_fss_directory_view
from Products.Silva import roleinfo
from Products.SilvaExternalSources.codesources import configure

manage_permission = 'Manage CodeSource Services'
logger = logging.getLogger('silva.externalsources')


def is_installed(root):
    # Hack to get installed state of this extension
    return hasattr(root.service_views, 'SilvaExternalSources')


def install(root):
    add_fss_directory_view(
        root.service_views, 'SilvaExternalSources', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)
    # metadata registration
    setupMetadata(root)
    configureSecurity(root)
    configureAddables(root)

    # add service_codesources
    if not hasattr(root.aq_explicit, 'service_codesources'):
        factory = root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSourceService(
            'service_codesources', 'Code Sources')

    # add core Silva Code Sources
    codesources_path = os.path.join(package_home(globals()), 'codesources')
    install_codesources(root, codesources_path, configure.configuration)

    # install by default cs_toc and cs_citation
    for source_id in ['cs_toc', 'cs_citation',]:
        if not hasattr(root.aq_explicit, source_id) and \
                hasattr(root.service_codesources.aq_explicit, source_id):
            token = root.service_codesources.manage_copyObjects([source_id,])
            root.manage_pasteObjects(token)



def uninstall(root):
    cs_fields = configure.configuration
    unregisterViews(root.service_view_registry)
    if not hasattr(root, 'service_codesources'):
        root.service_views.manage_delObjects(['SilvaExternalSources'])
    else:
        root.service_views.manage_delObjects(['SilvaExternalSources'])
        for cs_name, cs_element in cs_fields.items():
            if cs_element['id'] in root.service_codesources.objectIds():
                root.service_codesources.manage_delObjects([cs_element['id']])


def registerViews(reg):
    """Register core views on registry.
    """
    # add
    reg.register('add', 'Silva CSV Source', ['add', 'CSVSource'])
    # edit
    reg.register('edit', 'Silva CSV Source', ['edit', 'Asset', 'CSVSource'])
    # public
    reg.register('public', 'Silva CSV Source', ['public', 'CSVSource'])


def unregisterViews(reg):
    """Unregister core views on registry.
    """
    # add
    reg.unregister('add', 'Silva CSV Source')
    # edit
    reg.unregister('edit', 'Silva CSV Source')
    # public

    reg.unregister('public', 'Silva CSV Source')


def configureSecurity(root):
    """Update the security tab settings to the Silva defaults.
    """
    add_permissions = ('Add Silva CSV Sources',)
    for add_permission in add_permissions:
        root.manage_permission(add_permission, roleinfo.AUTHOR_ROLES)


def setupMetadata(root):
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    tm = ({'type': 'Silva CSV Source', 'chain': 'silva-content, silva-extra'},)
    mapping.editMappings(default, tm)


def configureAddables(root):
    addables = ['Silva CSV Source']
    new_addables = root.get_silva_addables_allowed_in_container()
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_container(new_addables)


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
    form.set_xml(data.read())
    context.set_form(form)


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


def install_codesources(root, path, sources, product_name=None):
    """Install a set of file-system code sources.
    """
    factory = root.service_codesources.manage_addProduct['SilvaExternalSources']
    for name, info in sources.items():
        factory.manage_addCodeSource(
            info['id'], info['title'], info['render_id'])
        source = getattr(root.service_codesources, info['id'])
        if info['desc']:
            source.set_description(info['desc'])
        if info['cacheable']:
            source.set_is_cacheable(True)
        if info['elaborate']:
            source.set_elaborate(True)

        codesource_path = os.path.join(path, info['id'])
        for filename in os.listdir(codesource_path):
            name, extension = os.path.splitext(filename)
            installer = INSTALLERS.get(extension, None)
            if installer is None:
                logger.info(
                    u"don't know how to install file %s for code source %s" % (
                        filename, info['id']))
                continue
            with open(os.path.join(codesource_path, filename), 'rb') as data:
                installer(source, data, name)



