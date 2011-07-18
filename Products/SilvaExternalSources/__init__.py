# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

silvaconf.extension_name('SilvaExternalSources')
silvaconf.extension_title('Silva External Sources')
silvaconf.extension_default()

logger = logging.getLogger('silva.externalsources')


class IExtension(Interface):
    """Silva External Sources extension.
    """

class ExternalSourcesInstaller(DefaultInstaller):
    """Silva External Sources installer
    """

    def install_custom(self, root):
        installed_ids = root.objectIds()
        if 'service_codesources' not in installed_ids:
            factory = root.manage_addProduct['SilvaExternalSources']
            factory.manage_addCodeSourceService()

        service = root.service_codesources
        for source_id in ['cs_toc', 'cs_citation',]:
            if source_id not in installed_ids:
                source = service.get_installable_source(source_id)
                if source is not None:
                    source.install(root)
                else:
                    logger.error(
                        u"could not find default source %s to install it." % (
                            source_id))


    def uninstall_custom(self, root):
        installed_ids = root.objectIds()
        if 'service_codesources' in installed_ids:
            root.manage_delObjects(['service_codesources'])


install = ExternalSourcesInstaller('SilvaExternalSources', IExtension)
