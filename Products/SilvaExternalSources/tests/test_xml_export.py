# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.silvaxml.xmlexport import exportToString
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase
from Products.SilvaExternalSources.testing import FunctionalLayer
from zope.publisher.browser import TestRequest


HTML_CODE_SOURCE = u"""
<div>
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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentExportTestCase))
    return suite
