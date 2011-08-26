# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import lxml.html
from lxml.cssselect import CSSSelector as css

from zope.publisher.browser import TestRequest
from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances
from Products.SilvaExternalSources.testing import FunctionalLayer


class CodeSourceDocumentImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_code_source(self):
        self.import_file(
            'test_import_code_source.silvaxml',
            globs=globals())
        doc = self.root.example
        version = doc.get_editable()
        self.assertTrue(version)
        sources = ISourceInstances(version.body)
        self.assertEquals(1, len(sources.keys()))
        tree = lxml.html.fragment_fromstring(version.body.render(
            version, TestRequest()))
        es = css("div.external-source")(tree)[0]
        self.assertEquals(css("div.author")(es)[0].text, u'ouam')
        self.assertEquals(css("div.source")(es)[0].text, u'wikipedia')
        self.assertEquals(css("div.citation")(es)[0].text.strip(),
            u'blahblahblah')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceDocumentImportTestCase))
    return suite
