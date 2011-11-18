# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.component import queryUtility

from Products.SilvaExternalSources.testing import FunctionalLayer
from Products.SilvaExternalSources.interfaces import ICodeSourceService
from Products.SilvaExternalSources.interfaces import ICodeSourceInstaller


class ServiceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_service(self):
        """Verify that the service implements the correct interfaces.
        """
        service = queryUtility(ICodeSourceService)
        self.assertTrue(verifyObject(ICodeSourceService, service))
        self.assertTrue('service_codesources' in self.root.objectIds())
        self.assertEqual(service, self.root.service_codesources)

    def test_default_installed_sources(self):
        """Verify installed sources. By default it should cs_toc and
        cs_citation.
        """
        self.assertTrue('cs_citation' in self.root.objectIds())
        self.assertTrue('cs_toc' in self.root.objectIds())

        service = queryUtility(ICodeSourceService)
        self.assertItemsEqual(
            list(service.get_installed_sources()),
            [self.root.cs_citation, self.root.cs_toc])

        # We can get the installable and they will tell us the same
        installable = service.get_installable_source(identifier='cs_citation')
        self.assertTrue(installable.is_installed(self.root), True)
        installable = service.get_installable_source(identifier='cs_toc')
        self.assertTrue(installable.is_installed(self.root), True)

    def test_clear_and_find_installed_sources(self):
        """Clear and find again installed code sources.
        """
        service = queryUtility(ICodeSourceService)
        installed = list(service.get_installed_sources())
        self.assertEqual(len(installed), 2)

        service.clear_installed_sources()
        installed = list(service.get_installed_sources())
        self.assertEqual(len(installed), 0)

        service.find_installed_sources()
        installed = list(service.get_installed_sources())
        self.assertEqual(len(installed), 2)

    def test_install_source(self):
        """Install cs_portlet_element, a default code source into a
        folder.
        """
        service = queryUtility(ICodeSourceService)
        installable = service.get_installable_source(
            identifier='cs_portlet_element')
        self.assertTrue(verifyObject(ICodeSourceInstaller, installable))
        self.assertEqual(
            installable.identifier,
            'cs_portlet_element')
        self.assertEqual(
            installable.location,
            'Products.SilvaExternalSources:/Products/SilvaExternalSources/codesources/cs_portlet_element')
        self.assertEqual(installable.validate(), True)

        # By default this source is not installed
        self.assertEqual(installable.is_installed(self.root), False)
        self.assertEqual(installable.is_installed(self.root.folder), False)

        # We can install it.
        installable.install(self.root.folder)

        # And it is installed
        self.assertEqual(installable.is_installed(self.root), False)
        self.assertEqual(installable.is_installed(self.root.folder), True)
        self.assertTrue('cs_portlet_element' in self.root.folder.objectIds())

        # And the location matches the one of the installer
        installed = self.root.folder.cs_portlet_element
        self.assertEqual(installable.location, installed.get_fs_location())

        # The source appears in the service as well
        self.assertItemsEqual(
            list(service.get_installed_sources()),
            [self.root.cs_citation, self.root.cs_toc, installed])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceTestCase))
    return suite

