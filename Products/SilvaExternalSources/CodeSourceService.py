# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from OFS.Folder import Folder

from Products.SilvaExternalSources.interfaces import ICodeSource
from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.SilvaExternalSources.interfaces import ICodeSourceService

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from five import grok
from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf
from silva.core.interfaces import IContainer
from silva.core.views import views as silvaviews
from silva.core.services.utils import walk_silva_tree

logger = logging.getLogger('silva.externalsources')


class CodeSourceService(Folder, SilvaService):
    meta_type = 'Silva Code Source Service'

    grok.implements(ICodeSourceService)
    grok.name('service_codesources')
    silvaconf.icon('www/codesource_service.png')

    manage_options = (
        {'label':'Code Sources', 'action':'manage_codesources'},
        ) + Folder.manage_options

    security = ClassSecurityInfo()
    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = DTMLFile('www/serviceCodeSourceEditTab', globals())

    _installed_sources = []

    def find_installed_sources(self):
        logger.info('search for code sources')
        self.clear_installed_sources()
        service = getUtility(IIntIds)
        for container in walk_silva_tree(self.get_root(), requires=IContainer):
            for content in container.objectValues():
                if ICodeSource.providedBy(content):
                    self._installed_sources.append(service.register(content))

    def get_installed_sources(self):
        resolve = getUtility(IIntIds).getObject
        return (resolve(id) for id in self._installed_sources)

    def clear_installed_sources(self):
        self._installed_sources = []


InitializeClass(CodeSourceService)


class ManageCodeSources(silvaviews.ZMIView):
    grok.name('manage_codesources')

    def update(self, find=False, clear=False):
        if clear:
            self.context.clear_installed_sources()
        if find:
            self.context.find_installed_sources()

        self.sources = []
        for source in self.context.get_installed_sources():
            self.sources.append({'id': source.getId(),
                                 'broken': source.is_broken(),
                                 'title': source.get_title(),
                                 'path': '/'.join(source.getPhysicalPath()),
                                 'url': source.absolute_url()})
