"""Install for Silva External Sources extension
"""

from Products.Silva.install import add_fss_directory_view
from Products.Silva import roleinfo

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

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaExternalSources'])


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
