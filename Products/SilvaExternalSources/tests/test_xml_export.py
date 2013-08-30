# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from Products.Silva.testing import TestRequest, Transaction
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase

from zeam.form import silva as silvaforms
from zeam.component import getWrapper

from ..testing import FunctionalLayer
from ..interfaces import IExternalSourceManager


HTML_CITATION_CODE_SOURCE = u"""
<div>
    <h1>Example</h1>
    <p>some paragraph..</p>
    <div class="external-source default"
         data-silva-name="cs_citation"
         data-silva-settings="field_citation=blahblahblah&amp;field_author=ouam&amp;field_source=wikipedia">
    </div>
</div>
"""
HTML_TOC_CODE_SOURCE = u"""
<div>
    <h1>Document with TOCs</h1>
    <p>A first table of content:</p>
    <div class="external-source default"
         data-silva-name="cs_toc"
         data-silva-settings="field_paths={0}&amp;field_toc_types=Silva+Folder&amp;field_depth=0&amp;field_sort_on=silva&amp;field_order=normal">
    </div>
    <p>Since we were not sure about it, a second table of content:</p>
    <div class="external-source default"
         data-silva-name="cs_toc"
         data-silva-settings="field_paths={0}&amp;field_toc_types=Silva+Folder&amp;field_depth=0&amp;field_sort_on=silva&amp;field_order=normal">
    </div>
</div>
"""

class TOCCodeSourceDocumentExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        with Transaction():
            self.layer.login('author')
            # You have to install the source as manager
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            factory = self.root.folder.manage_addProduct['silva.app.document']
            factory.manage_addDocument('example', 'Example')
            version = self.root.folder.example.get_editable()
            html = HTML_TOC_CODE_SOURCE.format(
                getUtility(IIntIds).register(self.root.folder))
            version.body.save(version, TestRequest(), html)

    def test_export_two_tocs_in_document(self):
        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source_two_tocs.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])


class CitationCodeSourceDocumentExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        with Transaction():
            self.layer.login('manager')
            # You have to install the source as manager
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            token = self.root.manage_cutObjects(['cs_citation'])
            self.root.folder.manage_pasteObjects(token)
        with Transaction():
            self.layer.login('author')
            # Continue as author
            factory = self.root.folder.manage_addProduct['silva.app.document']
            factory.manage_addDocument('example', 'Example')
            version = self.root.folder.example.get_editable()
            version.body.save(version, TestRequest(), HTML_CITATION_CODE_SOURCE)

    def test_export_code_source_and_document(self):
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

    def test_export_document_with_missing_source(self):
        """Export a document containing a missing code source.
        """
        with Transaction():
            # Delete code source to break it.
            self.root.manage_delObjects(['cs_citation'])
            self.root.folder.manage_delObjects(['cs_citation'])

        # Export
        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source_missing.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])

        version = self.root.folder.example.get_editable()
        self.assertEqual(
            exporter.getProblems(),
            [(u'Broken source in document while exporting: '
              u'source is no longer installed in the Silva site.',
              version)])


class SourceAssertExportTestCase(SilvaXMLTestCase):
    """Test source asset XML export. We will use the TOC code source
    for the test.
    """

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        with Transaction():
            self.layer.login('editor')
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            factory.manage_addFolder('other', 'Other Folder')
            factory = self.root.folder.manage_addProduct['SilvaExternalSources']
            factory.manage_addSourceAsset('asset', 'A source asset')

    def save_asset(self, target=None):
        with Transaction():
            # Helper to save the parameters in the test source asset.
            version = self.root.folder.asset.get_editable()

            if target is not None:
                target = getUtility(IIntIds).register(target)
            else:
                target = '0'
            request = TestRequest(
                form={'field_paths': str(target),
                      'field_toc_types': "Silva Folder",
                      'field_depth': "0",
                      'field_sort_on': "silva",
                      'field_order': "normal"})
            factory = getWrapper(version, IExternalSourceManager)
            source = factory(request, name='cs_toc')
            marker = source.create()
            version.set_parameters_identifier(source.getId())
        self.assertIs(marker, silvaforms.SUCCESS)
        return version

    def test_export_source_asset(self):
        self.save_asset(self.root.folder)

        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source_asset.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_export_source_asset_external_reference(self):
        """The code source has a parameters that will trigger an
        external reference error.
        """
        self.save_asset(self.root.other)

        self.assertExportFail(self.root.folder)

    def test_export_source_asset_external_reference_force(self):
        """The code source has a parameters that have a reference
        outside of the export, but the option external_references is
        set.
        """
        version = self.save_asset(self.root.other)

        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_source_asset_external.silvaxml',
            options={'external_references': True})
        self.assertEqual(
            exporter.getZexpPaths(),
            [])
        self.assertEqual(
            exporter.getAssetPaths(),
            [])
        self.assertEqual(
            exporter.getProblems(),
            [(u"A reference field 'paths' refers to an content outside of the export (../other).",
              version)])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CitationCodeSourceDocumentExportTestCase))
    suite.addTest(unittest.makeSuite(TOCCodeSourceDocumentExportTestCase))
    suite.addTest(unittest.makeSuite(SourceAssertExportTestCase))
    return suite
