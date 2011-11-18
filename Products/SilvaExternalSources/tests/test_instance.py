# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.publisher.browser import TestRequest
from zope.interface.verify import verifyObject

from Products.Formulator.interfaces import IBoundForm
from Products.Silva.testing import TestCase
from Products.SilvaExternalSources.testing import FunctionalLayer
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances
from Products.SilvaExternalSources.editor.interfaces import ISourceParameters
from Products.SilvaExternalSources.editor.interfaces import IBoundSourceInstance

HTML_WORKING_SOURCE = u"""
<div>
    <div class="external-source default"
         data-silva-name="cs_citation"
         data-silva-settings="field_citation=je bent een klootzak&amp;field_author=jou&amp;field_source=wikipedia">
    </div>
</div>
"""
HTML_BROKEN_SOURCE = u"""
<div>
    <div class="external-source default"
         data-silva-name="cs_data"
         data-silva-settings="field_data=je bent een klootzak&amp;source_failover=1">
    </div>
</div>
"""


class CreateInstanceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

    def test_create_instance(self):
        content = self.root.example
        request = TestRequest()
        version = content.get_editable()
        version.body.save(version, request, HTML_WORKING_SOURCE)

        # This gives access to all the sources
        sources = ISourceInstances(version.body)
        self.assertTrue(verifyObject(ISourceInstances, sources))
        self.assertEqual(len(sources.keys()), 1)
        self.assertEqual(len(sources.values()), 1)
        key = sources.keys()[0]

        parameters = sources[key]
        self.assertTrue(verifyObject(ISourceParameters, parameters))
        self.assertIs(sources.values()[0], parameters)
        self.assertIs(sources.get(key), parameters)

        # A parameters store data
        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(parameters.citation, u'je bent een klootzak')
        self.assertEqual(parameters.author, u'jou')
        self.assertEqual(parameters.source, u'wikipedia')

        # You can bind parameters to a content and a request
        bound = sources.bind(key, version, request)
        self.assertTrue(verifyObject(IBoundSourceInstance, bound))
        self.assertEqual(bound.identifier, 'cs_citation')
        source, form = bound.get_source_and_form()
        self.assertEqual(source, self.root.cs_citation)
        self.assertTrue(verifyObject(IBoundForm, form))

    def test_create_broken_failover(self):
        content = self.root.example
        request = TestRequest()
        version = content.get_editable()
        version.body.save(version, request, HTML_BROKEN_SOURCE)

        # This gives access to all the sources
        sources = ISourceInstances(version.body)
        self.assertTrue(verifyObject(ISourceInstances, sources))
        self.assertEqual(len(sources.keys()), 1)
        self.assertEqual(len(sources.values()), 1)
        key = sources.keys()[0]

        parameters = sources[key]
        self.assertTrue(verifyObject(ISourceParameters, parameters))
        self.assertIs(sources.values()[0], parameters)
        self.assertIs(sources.get(key), parameters)

        # A parameters store data
        self.assertEqual(parameters.get_source_identifier(), 'cs_data')

        # You can bind parameters to a content and a request
        bound = sources.bind(key, version, request)
        self.assertTrue(verifyObject(IBoundSourceInstance, bound))
        self.assertEqual(bound.identifier, 'cs_data')
        source, form = bound.get_source_and_form()
        self.assertEqual(source, None)
        self.assertEqual(form, None)


class WorkingInstanceTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

        version = self.root.example.get_editable()
        version.body.save(version, TestRequest(), HTML_WORKING_SOURCE)
        self.key = ISourceInstances(version.body).keys()[0]

    def test_render(self):
        version = self.root.example.get_editable()
        instances = ISourceInstances(version.body)
        bound = instances.bind(self.key, version, TestRequest())
        self.assertXMLEqual(bound.render(), """
<div class="citation">
 je bent een klootzak
 <div class="author">
  jou
 </div>
 <div class="source">
  wikipedia
 </div>
</div>
""")

    def test_remove(self):
        version = self.root.example.get_editable()
        instances = ISourceInstances(version.body)
        instances.remove(self.key, version, TestRequest())

        self.assertEqual(len(instances.keys()), 0)
        self.assertEqual(len(instances.values()), 0)
        self.assertEqual(instances.get(self.key), None)
        with self.assertRaises(KeyError):
            instances.bind(self.key, version, TestRequest())
        with self.assertRaises(KeyError):
            instances[self.key]

    def test_update(self):
        version = self.root.example.get_editable()
        instances = ISourceInstances(version.body)
        bound = instances.bind(self.key, version, TestRequest())
        bound.update('field_citation=il fait soleil&amp;field_author=moi')

        parameters = instances[self.key]
        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(parameters.citation, u'il fait soleil')
        self.assertEqual(parameters.author, u'moi')
        self.assertEqual(parameters.source, u'')
        self.assertXMLEqual(bound.render(), """
<div class="citation">
 il fait soleil
 <div class="author">
  moi
 </div>
 <div class="source">
 </div>
</div>
""")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CreateInstanceTestCase))
    suite.addTest(unittest.makeSuite(WorkingInstanceTestCase))
    return suite

