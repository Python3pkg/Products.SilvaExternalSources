# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from Products.Silva.testing import TestRequest
from Products.Silva.silvaxml.xmlexport import exportToString
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
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        token = self.root.manage_cutObjects(['cs_citation'])
        self.root.folder.manage_pasteObjects(token)
        self.layer.login('author')

    def test_code_source_and_document(self):
        content = self.root.folder.example
        version = content.get_editable()
        version.body.save(version, TestRequest(), HTML_CODE_SOURCE)

        xml, info = exportToString(self.root.folder)
        self.assertExportEqual(
            xml, 'test_export_source.silvaxml', globs=globals())


class SourceAssertExportTestCase(SilvaXMLTestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.folder = self.root._getOb('folder')

        factory = self.folder.manage_addProduct['SilvaExternalSources']
        factory.manage_addSourceAsset('asset', 'A source asset')

        self.source_asset = self.folder._getOb('asset')
        self.source_asset_version = self.source_asset.get_editable()

        folder_id = getUtility(IIntIds).register(self.folder)
        request = TestRequest(
            form={'field_paths': str(folder_id),
                  'field_toc_types': "Silva Folder",
                  'field_depth': "0",
                  'field_sort_on': "silva",
                  'field_order': "normal"})
        factory = getWrapper(self.source_asset_version,
                             IExternalSourceManager)
        source = factory(request, name='cs_toc')
        marker = source.create()
        self.source_asset_version.set_parameters_identifier(source.getId())
        assert silvaforms.SUCCESS == marker

    def test_export_source_asset(self):
        xml, _ = exportToString(self.folder)
        self.assertExportEqual(xml, 'test_export_source_asset.silvaxml',
                               globals())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentExportTestCase))
    suite.addTest(unittest.makeSuite(SourceAssertExportTestCase))
    return suite
