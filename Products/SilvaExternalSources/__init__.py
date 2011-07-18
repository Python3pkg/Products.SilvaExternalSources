# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

silvaconf.extension_name('SilvaExternalSources')
silvaconf.extension_title('Silva External Sources')
silvaconf.extension_default()


class IExtension(Interface):
    """Silva External Sources extension.
    """

class SilvaExternalSourcesInstaller(DefaultInstaller):
    """Silva External Sources installer
    """

    def install_custom(self, root):
        installed_ids = root.objectIds()
        if 'service_codesources' not in installed_ids:
            factory = root.manage_addProduct['SilvaExternalSources']
            factory.manage_addCodeSourceService()

        for source_id in ['cs_toc', 'cs_citation',]:
            if source_id not in installed_ids:
                source = root.service_codesources.get_installable_source(source_id)
                source.install(root)


    def uninstall_custom(self, root):
        if 'service_codesources' in root.objectdIds():
            root.manage_delObjects(['service_codesources'])


installer = SilvaExternalSourcesInstaller('SilvaExternalSources', IExtension)
