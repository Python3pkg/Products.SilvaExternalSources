# Copyright (c) 2006-2010 Infrae
# All rights reserved. See also LICENSE.txt
# $Id$

# Python
import logging
# Zope
from zope.interface import implements
# Silva
from silva.core.interfaces import IUpgrader
from silva.core.upgrade import upgrade

_extsources_version = '1.5.8'

class SourceTitleUpgrader:

    implements(IUpgrader)

    def upgrade(self, obj):
        title = obj.title
        if type(title) == type(u''):
            return obj
        obj.title = unicode(title, obj.management_page_charset)
        return obj

extSourcesUpgradeRegistry = upgrade.UpgradeRegistry()
extSourcesUpgradeRegistry.registerUpgrader(
    SourceTitleUpgrader(), _extsources_version, 'Silva Code Source')
extSourcesUpgradeRegistry.registerUpgrader(
    SourceTitleUpgrader(), _extsources_version, 'Silva CSV Source')
extSourcesUpgradeRegistry.registerUpgrader(
    SourceTitleUpgrader(), _extsources_version, 'Silva SQL Source')


def upgrade_extsources(container=None):
    if not container:
        return "No silva object provided"

    silva_root = container.get_root()
    if not silva_root:
        msg = "No Silva root found for Silva External Sources upgrade %s"
        return msg  % _extsources_version

    extSourcesUpgradeRegistry.upgradeTree(silva_root, _extsources_version)
    return 'done'
