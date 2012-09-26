# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.publisher.browser import TestRequest
from zope.interface.verify import verifyObject
from zeam.component import getWrapper

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase

from silva.app.document.interfaces import IDocument
from silva.core.interfaces.events import IContentImported
from silva.core.references.reference import ReferenceSet

from ..interfaces import IExternalSourceManager
from ..interfaces import ISourceAsset, ISourceAssetVersion
from ..testing import FunctionalLayer


class CodeSourceDocumentImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_document(self):
        """Import a document that uses a source.
        """
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
        sources = getWrapper(version, IExternalSourceManager)
        keys = list(sources.all())
        self.assertEqual(len(keys), 1)
        parameters, source = sources.get_parameters(instance=keys[0])
        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(source.id, 'cs_citation')
        self.assertEqual(parameters.citation, u"héhé l'aime le quéqué")
        self.assertEqual(parameters.author, u'ouam')
        self.assertEqual(parameters.source, u'wikipedia')

    def test_document_missing_source(self):
        """Import a document that uses a source that is missing on the
        system.

        The document is imported, but not the source.
        """
        self.import_file(
            'test_import_source_missing.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/example'],
            IContentImported)

        document = self.root.example
        self.assertTrue(verifyObject(IDocument, document))
        self.assertEqual(document.get_viewable(), None)
        self.assertNotEqual(document.get_editable(), None)

        version = document.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 0)


class SourceAssetImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_source_asset(self):
        self.import_file('test_import_source_asset.silvaxml', globals())

        asset = self.root.folder.asset
        self.assertTrue(verifyObject(ISourceAsset, asset))
        version = asset.get_editable()
        self.assertTrue(verifyObject(ISourceAssetVersion, version))
        source = version.get_controller(TestRequest())
        self.assertEquals('cs_toc', source.getSourceId())
        params, _ = source.manager.get_parameters(version._parameter_identifier)
        self.assertIn(self.root.folder, ReferenceSet(version, params.paths))
        self.assertEquals(set(['Silva Folder']), set(params.toc_types))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentImportTestCase))
    suite.addTest(unittest.makeSuite(SourceAssetImportTestCase))
    return suite
