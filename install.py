"""Install for Silva External Sources extension
"""
# Python
import os
import os.path
from warnings import warn

# Zope
from Globals import package_home
from zExceptions import BadRequest
from Products.Formulator.Form import ZMIForm

# Silva
from Products.Silva.install import add_fss_directory_view
from Products.Silva import roleinfo
from Products.SilvaExternalSources.CodeSources import configure

manage_permission = 'Manage CodeSource Services'

def read_file(filename):
    f = open(filename, 'rb')
    text = f.read()
    f.close()
    return text

def is_installed(root):
    # Hack to get installed state of this extension
    return hasattr(root.service_views, 'SilvaExternalSources')

def install(root):
    # Hack - refresh SilvaDocument to make it pick up this extension
    root.service_extensions.refresh('SilvaDocument')
    add_fss_directory_view(root.service_views, 'SilvaExternalSources', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)
    # metadata registration
    setupMetadata(root)
    configureSecurity(root)
    configureAddables(root)
    # add service_codesources
    if not hasattr(root, 'service_codesources'):
        root.manage_addProduct['SilvaExternalSources'].manage_addCodeSourceService(
            'service_codesources', 'Code Sources')
    # add core Silva Code Sources
    cs_fields = configure.configuration
    path_join = os.path.join
    _fs_codesources_path = path_join(package_home(globals()), 'CodeSources')
    install_codesources(_fs_codesources_path, root, cs_fields)

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
    tm = (
            {'type': 'Silva CSV Source', 'chain': 'silva-content, silva-extra'},
        )
    mapping.editMappings(default, tm)


def configureAddables(root):
    addables = ['Silva CSV Source']
    new_addables = root.get_silva_addables_allowed_in_publication()
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_publication(new_addables)

def install_codesources(cs_path, root, cs_fields, product_name=None):
    clean_path = cs_path
    for cs_name, cs_element in cs_fields.items():
        # Backward compatibility, render_id was called before script_id
        render_id = cs_element.get('render_id', None)
        if not render_id:
            render_id = cs_element.get('script_id')
            warn('Please update your code source to define render_id instead of script_id', DeprecationWarning)
            
        root.service_codesources.manage_addProduct[
            'SilvaExternalSources'].manage_addCodeSource(cs_element['id'],
                                                         cs_element['title'],
                                                         render_id)
        cs = getattr(root.service_codesources, cs_element['id'])
        if cs_element['desc']:
            cs.set_description(cs_element['desc'])
        cs_path = os.path.join(cs_path, cs_element['dirname'])            
        if root.service_codesources.hasObject(cs_element['id']):
            if cs_element['script']:
                cs.manage_addProduct['PythonScripts'].manage_addPythonScript(
                    cs_element['script'])
                cs_code = getattr(cs, cs_element['script'])
                script_path = os.path.join(cs_path, cs_element['script'])
                cs_code.write(read_file(script_path))
            if cs_element['template']:
                cs_code = cs.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                    cs_element['template'])
                template_path = os.path.join(cs_path, cs_element['template'])
                cs_code.pt_edit(read_file(template_path), '')
            if cs_element['form']:
                form_path = os.path.join(cs_path, cs_element['form'])
                form = ZMIForm('form', 'Parameters form')
                form.set_xml(read_file(form_path))
                cs_code.set_form(form)
            if cs_element['history']:
                cs_code = cs.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                    cs_element['history'])
                history_path = os.path.join(cs_path, cs_element['history'])
                cs_code.pt_edit(read_file(history_path), '')
            if cs_element['license']:
                cs_code = cs.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                    cs_element['license'])
                license_path = os.path.join(cs_path, cs_element['license'])
                cs_code.pt_edit(read_file(license_path), '')
            if cs_element['readme']:
                cs_code = cs.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                    cs_element['readme'])
                readme_path = os.path.join(cs_path, cs_element['readme'])
                cs_code.pt_edit(read_file(readme_path), '')
            if cs_element['version']:
                cs_code = cs.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                    cs_element['version'])
                version_path = os.path.join(cs_path, cs_element['version'])
                cs_code.pt_edit(read_file(version_path), '')
        cs_path = clean_path

