# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances
from Products.SilvaExternalSources.testing import FunctionalLayer
from silva.core.interfaces.events import IContentImported
from silva.app.document.interfaces import IDocument


class CodeSourceDocumentImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_code_source(self):
        self.import_file(
            'test_import_source.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/example'],
            IContentImported)

        document = self.root.example
        self.assertTrue(verifyObject(IDocument, document))
        self.assertEqual(document.get_viewable(), None)
        self.assertNotEqual(document.get_editable(), None)

        version = document.get_editable()
        sources = ISourceInstances(version.body)
        self.assertEquals(len(sources.keys()), 1)
        instance = sources.values()[0]
        self.assertEqual(instance.get_source_identifier(), 'cs_citation')
        self.assertEqual(instance.citation, u"héhé l'aime le quéqué")
        self.assertEqual(instance.author, u'ouam')
        self.assertEqual(instance.source, u'wikipedia')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentImportTestCase))
    return suite
