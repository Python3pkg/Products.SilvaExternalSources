"""Install for Silva External Sources extension
"""
def is_installed(root):
    # Hack to get installed state of this extension
    return hasattr(root.service_views, 'SilvaExternalSources')

def install(root):
    root.service_views.manage_addFolder('SilvaExternalSources')

def uninstall(root):
    root.service_views.manage_delObjects(['SilvaExternalSources'])
