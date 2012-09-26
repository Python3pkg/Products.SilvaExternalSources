# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

silvaconf.extension_name('SilvaExternalSources')
silvaconf.extension_title('Silva External Sources')
silvaconf.extension_depends(["Silva", "silva.core.editor"])
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
        for identifier in ['cs_toc', 'cs_citation',]:
            if identifier not in installed_ids:
                candidates = list(
                    service.get_installable_source(identifier=identifier))
                if len(candidates) == 1:
                    candidates[0].install(root)
                else:
                    logger.error(
                        u"Could not find default source %s to install it.",
                        identifier)


    def uninstall_custom(self, root):
        installed_ids = root.objectIds()
        if 'service_codesources' in installed_ids:
            root.manage_delObjects(['service_codesources'])


install = ExternalSourcesInstaller('SilvaExternalSources', IExtension)


CLASS_CHANGES = {
    'Products.SilvaExternalSources.editor.instance SourceParameters':
        'Products.SilvaExternalSources.SourceInstance SourceParameters',
    'Products.SilvaExternalSources.editor.instance SourceInstances':
        'Products.SilvaExternalSources.SourceInstance SourceInstances'
    }
