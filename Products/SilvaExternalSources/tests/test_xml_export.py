# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from Products.Silva.testing import TestRequest
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase

from zeam.form import silva as silvaforms
from zeam.component import getWrapper

from ..testing import FunctionalLayer
from ..interfaces import IExternalSourceManager


HTML_CODE_SOURCE = u"""
<div>
    <h1>Example</h1>
    <p>some paragraph..</p>
    <div class="external-source default"
         data-silva-name="cs_citation"
         data-silva-settings="field_citation=blahblahblah&amp;field_author=ouam&amp;field_source=wikipedia">
    </div>
</div>
"""


class CodeSourceDocumentExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        # You have to install the source as manager
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        token = self.root.manage_cutObjects(['cs_citation'])
        self.root.folder.manage_pasteObjects(token)
        self.layer.login('author')
        # Continue as author
        factory = self.root.folder.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        version = self.root.folder.example.get_editable()
        version.body.save(version, TestRequest(), HTML_CODE_SOURCE)

    def test_code_source_and_document(self):
        """Export a document containing a code source.

        The code source is exported as a ZEXP.
        """
        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source.silvaxml')
        self.assertEqual(
            exporter.getZexpPaths(),
            [(('', 'root', 'folder', 'cs_citation'), '1.zexp')])
        self.assertEqual(
            exporter.getAssetPaths(),
            [])
        self.assertEqual(
            exporter.getProblems(),
            [])

    def test_code_source_and_document_broken(self):
        """Export a document containing a broken code source.
        """
        # Delete code source to break it.
        self.root.manage_delObjects(['cs_citation'])
        self.root.folder.manage_delObjects(['cs_citation'])

        # Export
        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source_broken.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])

        version = self.root.folder.example.get_editable()
        self.assertEqual(
            exporter.getProblems(),
            [(u'Broken source in document: source is gone in the export.', version)])


class SourceAssertExportTestCase(SilvaXMLTestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['SilvaExternalSources']
        factory.manage_addSourceAsset('asset', 'A source asset')

        version = self.root.folder._getOb('asset').get_editable()

        folder_id = getUtility(IIntIds).register(self.root.folder)
        request = TestRequest(
            form={'field_paths': str(folder_id),
                  'field_toc_types': "Silva Folder",
                  'field_depth': "0",
                  'field_sort_on': "silva",
                  'field_order': "normal"})
        factory = getWrapper(version, IExternalSourceManager)
        source = factory(request, name='cs_toc')
        marker = source.create()
        version.set_parameters_identifier(source.getId())
        assert silvaforms.SUCCESS == marker

    def test_export_source_asset(self):
        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source_asset.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentExportTestCase))
    suite.addTest(unittest.makeSuite(SourceAssertExportTestCase))
    return suite
