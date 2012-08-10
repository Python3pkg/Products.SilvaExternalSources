# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zeam.component import getWrapper

from Products.Silva.testing import TestCase, TestRequest

from .. import errors
from ..interfaces import IExternalSourceController
from ..interfaces import IExternalSourceManager, IExternalSourceInstance
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


class CreationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

    def test_create_transform(self):
        """Create a new source instance, of an existing code source.
        """
        request = TestRequest()
        version = self.root.example.get_editable()
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
        self.assertEqual(parameters.get_parameter_identifier(), instance_key)
        self.assertEqual(source.id, 'cs_citation')
        self.assertEqual(parameters.citation, u'je bent een klootzak')
        self.assertEqual(parameters.author, u'jou')
        self.assertEqual(parameters.source, u'wikipedia')

        # You can bind parameters to a content and a request
        controller = sources(request, instance=instance_key)
        self.assertTrue(verifyObject(IExternalSourceController, controller))

    def test_create_transform_broken_failover(self):
        """Create a source that doesn't exists with failover. No
        source is created, but no error is yielded.
        """
        request = TestRequest()
        version = self.root.example.get_editable()
        version.body.save(version, request, HTML_BROKEN_SOURCE)

        # This gives access to all the sources
        sources = getWrapper(version, IExternalSourceManager)
        self.assertTrue(verifyObject(IExternalSourceManager, sources))
        self.assertEqual(len(sources.all()), 0)

    def test_create(self):
        """Create a source by hand.
        """
        request = TestRequest(form={
                'field_citation': 'je bent een hero',
                'field_author': 'u',
                'field_source': 'google',
                })
        version = self.root.example.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 0)

        controller = sources(request, name='cs_citation')
        # You cannot save or remove the source, it does not exist yet.
        with self.assertRaises(AssertionError):
            controller.save()
        with self.assertRaises(AssertionError):
            controller.remove()
        self.assertEqual(controller.getId(), None)

        # But you can create it, and it will created after.
        controller.create()
        self.assertNotEqual(controller.getId(), None)
        self.assertEqual(len(sources.all()), 1)
        instance_key = list(sources.all())[0]

        parameters, source = sources.get_parameters(instance=instance_key)
        self.assertTrue(verifyObject(IExternalSourceInstance, parameters))
        self.assertEqual(controller.getId(), instance_key)
        self.assertEqual(parameters.get_parameter_identifier(), instance_key)
        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(source.id, 'cs_citation')
        self.assertEqual(parameters.citation, u'je bent een hero')
        self.assertEqual(parameters.author, u'u')
        self.assertEqual(parameters.source, u'google')

    def test_create_broken(self):
        """Create a broken source: you can't access the create method.
        """
        request = TestRequest()
        version = self.root.example.get_editable()

        # This gives access to all the sources
        sources = getWrapper(version, IExternalSourceManager)
        self.assertTrue(verifyObject(IExternalSourceManager, sources))
        self.assertEqual(len(sources.all()), 0)

        with self.assertRaises(errors.SourceMissingError):
            sources.get_parameters()
        with self.assertRaises(errors.SourceMissingError):
            sources.get_parameters(name='cs_nonexisting')
        with self.assertRaises(errors.SourceMissingError):
            sources(request, name='cs_nonexisting')

        with self.assertRaises(errors.ParametersMissingError):
            sources.get_parameters(instance='nonexisting')
        with self.assertRaises(errors.ParametersMissingError):
            sources(request, instance='nonexisting')


class WorkingControllerTestCase(TestCase):
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

    def test_controller(self):
        """Test the controller API.
        """
        controller = self.sources(TestRequest(), instance=self.identifier)
        _, source = self.sources.get_parameters(instance=self.identifier)
        self.assertTrue(verifyObject(IExternalSourceController, controller))

        self.assertEqual(controller.getId(), self.identifier)
        self.assertEqual(controller.getSourceId(), 'cs_citation')
        self.assertEqual(controller.editable(), True) # The source have fields.
        self.assertEqual(controller.label, source.get_title())
        self.assertEqual(controller.description, source.get_description())

    def test_create(self):
        """You cannot recreate an existing source.
        """
        controller = self.sources(TestRequest(), instance=self.identifier)
        with self.assertRaises(AssertionError):
            controller.new()

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
        with self.assertRaises(errors.ParametersMissingError):
            self.sources.get_parameters(instance=self.identifier)
        with self.assertRaises(errors.ParametersMissingError):
            self.sources(TestRequest(), instance=self.identifier)

    def test_save(self):
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

    def test_save_unicode(self):
        """Updating source parameters, with unicode values.
        """
        request = TestRequest(form={
                'field_citation': u'Cela est éternel'.encode('utf-8'),
                'field_author': 'moi',
                'marker_field_citation': '1',
                'marker_field_author': '1',
                'marker_field_source': '1'})
        controller = self.sources(request, instance=self.identifier)
        controller.save()

        parameters, source = self.sources.get_parameters(
            instance=self.identifier)

        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(parameters.citation, u'Cela est éternel')
        self.assertEqual(parameters.author, u'moi')
        self.assertEqual(parameters.source, u'')
        self.assertXMLEqual(controller.render(), u"""
<div class="citation">
 Cela est éternel
 <div class="author">
  moi
 </div>
 <div class="source">
 </div>
</div>
""")


class BrokenControllerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

        # Create cs_data as a copy of cs_citation
        token = self.root.manage_copyObjects(['cs_citation'])
        self.root.manage_pasteObjects(token)
        self.root.manage_renameObject('copy_of_cs_citation', 'cs_data')

        # Create source.
        version = self.root.example.get_editable()
        version.body.save(version, TestRequest(), HTML_BROKEN_SOURCE)
        self.sources = getWrapper(version, IExternalSourceManager)
        self.identifier = list(self.sources.all())[0]

        # Remove source, that will break the instance.
        self.root.manage_delObjects(['cs_data'])

    def test_render(self):
        """Render a broken source, you will get an error.
        """
        controller = self.sources(TestRequest(), instance=self.identifier)
        with self.assertRaises(errors.SourceMissingError):
            controller.render()

    def test_remove(self):
        """Remove a broken source, this should work.
        """
        controller = self.sources(TestRequest(), instance=self.identifier)
        controller.remove()

        self.assertEqual(len(self.sources.all()), 0)
        with self.assertRaises(errors.ParametersMissingError):
            self.sources.get_parameters(instance=self.identifier)
        with self.assertRaises(errors.ParametersMissingError):
            self.sources(TestRequest(), instance=self.identifier)

    def test_save(self):
        """You cannot save values into a broken source.
        """
        request = TestRequest(
            form={'field_citation': 'il fait soleil',
                  'field_author': 'moi'})
        controller = self.sources(request, instance=self.identifier)
        with self.assertRaises(errors.SourceMissingError):
            controller.save()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CreationTestCase))
    suite.addTest(unittest.makeSuite(WorkingControllerTestCase))
    suite.addTest(unittest.makeSuite(BrokenControllerTestCase))
    return suite

