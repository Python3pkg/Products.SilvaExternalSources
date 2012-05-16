# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.publisher.browser import TestRequest
from zope.interface.verify import verifyObject
from zeam.component import getWrapper

from Products.Silva.testing import TestCase

from ..interfaces import IExternalSourceController
from ..interfaces import IExternalSourceManager, IExternalSourceInstance
from ..interfaces import ParametersMissingError
from ..testing import FunctionalLayer

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
        """Create a new source instance, of an existing code source.
        """
        content = self.root.example
        request = TestRequest()
        version = content.get_editable()
        version.body.save(version, request, HTML_WORKING_SOURCE)

        # This gives access to all the sources
        sources = getWrapper(version, IExternalSourceManager)
        self.assertTrue(verifyObject(IExternalSourceManager, sources))
        self.assertEqual(len(sources.all()), 1)
        instance_key = list(sources.all())[0]

        parameters, source = sources.get_parameters(instance=instance_key)
        self.assertTrue(verifyObject(IExternalSourceInstance, parameters))

        # A parameters store data
        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(source.id, 'cs_citation')
        self.assertEqual(parameters.citation, u'je bent een klootzak')
        self.assertEqual(parameters.author, u'jou')
        self.assertEqual(parameters.source, u'wikipedia')

        # You can bind parameters to a content and a request
        controller = sources(request, instance=instance_key)
        self.assertTrue(verifyObject(IExternalSourceController, controller))

    def test_create_broken_failover(self):
        """Create a source that doesn't exists with failover. Test the
        broken source instance.
        """
        content = self.root.example
        request = TestRequest()
        version = content.get_editable()
        version.body.save(version, request, HTML_BROKEN_SOURCE)

        # This gives access to all the sources
        sources = getWrapper(version, IExternalSourceManager)
        self.assertTrue(verifyObject(IExternalSourceManager, sources))
        self.assertEqual(len(sources.all()), 1)
        instance_key = list(sources.all())[0]

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
        self.sources = getWrapper(version, IExternalSourceManager)
        self.identifier = list(self.sources.all())[0]

    def test_render(self):
        """Render a defined source.
        """
        controller = self.sources(TestRequest(), instance=self.identifier)
        self.assertXMLEqual(controller.render(), """
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
        """Remove a defined source.
        """
        controller = self.sources(TestRequest(), instance=self.identifier)
        controller.remove()

        self.assertEqual(len(self.sources.all()), 0)
        with self.assertRaises(ParametersMissingError):
            self.sources.get_parameters(instance=self.identifier)
        with self.assertRaises(ParametersMissingError):
            self.sources(TestRequest(), instance=self.identifier)

    def test_update(self):
        """Updating source parameters.
        """
        request = TestRequest(form={
                'field_citation': 'il fait soleil',
                'field_author': 'moi',
                'marker_field_citation': '1',
                'marker_field_author': '1',
                'marker_field_source': '1'})
        controller = self.sources(request, instance=self.identifier)
        controller.save()

        parameters, source = self.sources.get_parameters(
            instance=self.identifier)

        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(parameters.citation, u'il fait soleil')
        self.assertEqual(parameters.author, u'moi')
        self.assertEqual(parameters.source, u'')
        self.assertXMLEqual(controller.render(), """
<div class="citation">
 il fait soleil
 <div class="author">
  moi
 </div>
 <div class="source">
 </div>
</div>
""")


class BrokenInstanceTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

        version = self.root.example.get_editable()
        version.body.save(version, TestRequest(), HTML_BROKEN_SOURCE)
        self.key = ISourceInstances(version.body).keys()[0]

    def test_render(self):
        """Render a broken source.
        """
        version = self.root.example.get_editable()
        instances = ISourceInstances(version.body)
        bound = instances.bind(self.key, version, TestRequest())
        self.assertXMLEqual(bound.render(), """
<p>
 Source is missing
</p>
""")

    def test_remove(self):
        """Remove a broken source.
        """
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
        """Try to upgrade a broken source parameters.
        """
        version = self.root.example.get_editable()
        instances = ISourceInstances(version.body)
        bound = instances.bind(self.key, version, TestRequest())
        with self.assertRaises(ValueError):
            bound.update('field_citation=il fait soleil&amp;field_author=moi')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CreateInstanceTestCase))
    suite.addTest(unittest.makeSuite(WorkingInstanceTestCase))
    suite.addTest(unittest.makeSuite(BrokenInstanceTestCase))
    return suite

