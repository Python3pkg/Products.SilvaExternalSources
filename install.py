"""Install for Silva External Sources extension
"""
def is_installed(root):
    # Hack to get installed state of this extension
    return hasattr(root.service_views, 'SilvaExternalSources')

def install(root):
    # Hack - refresh SilvaDocument to make it pick up this extension
    root.service_extensions.refresh('SilvaDocument')
    root.service_views.manage_addFolder('SilvaExternalSources')

def uninstall(root):
    root.service_views.manage_delObjects(['SilvaExternalSources'])
