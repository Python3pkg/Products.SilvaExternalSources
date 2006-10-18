# Copyright (c) 2006, Infrae
# All rights reserved. See also LICENSE.txt

# Python
import logging
# Zope
from zope.interface import implements
# Silva
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade

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
        return "No Silva root found for Silva External Sources upgrade %s" % _extsources_version

    extSourcesUpgradeRegistry.upgradeTree(silva_root, _extsources_version)
    return 'done'
