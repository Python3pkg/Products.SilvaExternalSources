"""Install for Silva External Sources extension
"""

from Products.Silva.install import add_fss_directory_view


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

def setupMetadata(root):
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    tm = (
            {'type': 'Silva CSV Source', 'chain': 'silva-content, silva-extra'},
        )
    mapping.editMappings(default, tm)


