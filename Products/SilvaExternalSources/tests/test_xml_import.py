# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.publisher.browser import TestRequest
from zope.interface.verify import verifyObject
from zeam.component import getWrapper

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase

from silva.app.document.interfaces import IDocument
from silva.core.references.reference import ReferenceSet

from ..errors import SourceMissingError
from ..interfaces import IExternalSourceManager
from ..interfaces import ISourceAsset, ISourceAssetVersion
from ..testing import FunctionalLayer


class CodeSourceDocumentImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_document_with_source(self):
        """Import a document that uses a source.
        """
        importer = self.assertImportFile(
            'test_import_source.silvaxml',
            ['/root/example'])
        self.assertEqual(importer.getProblems(), [])

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
        self.assertEqual(parameters.citation, "héhé l'aime le quéqué")
        self.assertEqual(parameters.author, 'ouam')
        self.assertEqual(parameters.source, 'wikipedia')

    def test_document_with_missing_source(self):
        """Import a document that uses a source that is missing on the
        system.

        The document is imported, but not the source.
        """
        importer = self.assertImportFile(
            'test_import_source_missing.silvaxml',
            ['/root/example'])

        document = self.root.example
        self.assertTrue(verifyObject(IDocument, document))
        self.assertEqual(document.get_viewable(), None)
        self.assertNotEqual(document.get_editable(), None)

        version = document.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 0)
        self.assertEqual(
            importer.getProblems(),
            [('Broken source in import: '
              'External Source cs_ultimate is not available.', version)])


class SourceAssetImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_source_asset(self):
        importer = self.assertImportFile(
            'test_import_source_asset.silvaxml',
            ['/root/folder',
             '/root/folder/asset'])
        self.assertEqual(importer.getProblems(), [])

        asset = self.root.folder.asset
        self.assertTrue(verifyObject(ISourceAsset, asset))
        version = asset.get_editable()
        self.assertTrue(verifyObject(ISourceAssetVersion, version))
        source = version.get_source()
        self.assertEquals('cs_toc', source.getId())
        params = version.get_parameters()
        self.assertIn(self.root.folder, ReferenceSet(version, params.paths))
        self.assertEquals(set(['Silva Folder']), set(params.toc_types))

    def test_source_asset_missing_source(self):
        """Import a source asset content that uses a unexisting
        source.
        """
        importer = self.assertImportFile(
            'test_import_source_asset_missing.silvaxml',
            ['/root/folder',
             '/root/folder/asset'])

        asset = self.root.folder.asset
        self.assertTrue(verifyObject(ISourceAsset, asset))
        version = asset.get_editable()
        self.assertTrue(verifyObject(ISourceAssetVersion, version))
        with self.assertRaises(SourceMissingError):
            version.get_source()

        self.assertEqual(
            importer.getProblems(),
            [('Broken source in import: '
              'External Source cs_missing is not available.', version)])

    def test_source_asset_invalid_parameters(self):
        """Import a source asset content with invalid parameters.
        """
        importer = self.assertImportFile(
            'test_import_source_asset_invalid_parameters.silvaxml',
            ['/root/folder',
             '/root/folder/asset'])

        asset = self.root.folder.asset
        self.assertTrue(verifyObject(ISourceAsset, asset))
        version = asset.get_editable()
        self.assertTrue(verifyObject(ISourceAssetVersion, version))
        source = version.get_source()
        self.assertEquals(source.getId(), 'cs_toc')
        params = version.get_parameters()
        self.assertEqual(set(params.toc_types), set(['Silva Folder']))
        self.assertEqual(
            importer.getProblems(),
            [("Error in field 'paths': Could not resolve imported path non/existant.", version),
             ("Error in field 'paths': Broken reference.", version)])

    def test_source_asset_unknown_parameters(self):
        """This export contains extra unknown parameters.
        """
        importer = self.assertImportFile(
            'test_import_source_asset_unknown_parameters.silvaxml',
            ['/root/folder',
             '/root/folder/asset'])
        self.assertEqual(importer.getProblems(), [])

        asset = self.root.folder.asset
        self.assertTrue(verifyObject(ISourceAsset, asset))
        version = asset.get_editable()
        self.assertTrue(verifyObject(ISourceAssetVersion, version))
        source = version.get_source()
        self.assertEqual(source.getId(), 'cs_toc')
        params = version.get_parameters()
        self.assertIn(self.root.folder, ReferenceSet(version, params.paths))
        self.assertEqual(set(params.toc_types), set(['Silva Folder']))
        self.assertIs(getattr(params, 'space_depth', None), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentImportTestCase))
    suite.addTest(unittest.makeSuite(SourceAssetImportTestCase))
    return suite
