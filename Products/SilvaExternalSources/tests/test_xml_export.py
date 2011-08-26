# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.tests.test_xml_export import SilvaXMLTestCase
from Products.SilvaExternalSources.testing import FunctionalLayer


from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest


from silva.core.editor.transform.interfaces import (
    ITransformer, ISaveEditorFilter)

class CodeSourceDocumentExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer


    html = u"""
<div>
    <p>some paragraph..</p>
    <div class="external-source default"
         data-silva-name="cs_citation"
         data-silva-settings="field_citation=blahblahblah&amp;field_author=ouam&amp;field_source=wikipedia">
    </div>
</div>
"""

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        self.content = self.root.example
        self.version = self.content.get_editable()
        transformer = getMultiAdapter(
            (self.version, TestRequest()), ITransformer)
        self.version.body.save_raw_text(transformer.data(
            'body',
            self.version.body,
            self.html,
            ISaveEditorFilter))


    def test_export_code_sources(self):
        xml_string, _ = exportToString(self.root)
        tree = lxml.etree.fromstring(xml_string)
        # print lxml.etree.tostring(tree, pretty_print=True)
        ns = {'e': "http://infrae.com/namespace/silva-core-editor",
            'cs': "http://infrae.com/namespace/Products.SilvaExternalSources",
            'html': XHTML_NS}
        sel = '//html:div[contains(@class, "external-source")]'
        nodes = tree.xpath(sel, namespaces=ns)
        self.assertEquals(1, len(nodes))
        source = nodes[0]
        self.assertEquals('cs_citation', source.attrib['source-path'])
        fields = source.xpath('./cs:fields/cs:field', namespaces=ns)
        self.assertEquals(3, len(fields))
        info = {}
        for field in fields:
            info[field.attrib['id']] = field.text
        self.assertEquals(
            set(['field-author', 'field-citation', 'field-source']),
            set(info.keys()))
        self.assertEquals('blahblahblah', info['field-citation'])
        self.assertEquals('ouam', info['field-author'])
        self.assertEquals('wikipedia', info['field-source'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentExportTestCase))
    return suite
