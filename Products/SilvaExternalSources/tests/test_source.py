# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import doctest

from zope.interface.verify import verifyObject
from zeam.component import getWrapper
from silva.core.views import views as silvaviews
from silva.core.interfaces import IFolder

from Products.Silva.testing import TestRequest

from ..interfaces import availableSources
from ..interfaces import ICodeSource, IExternalSource
from ..interfaces import IExternalSourceController
from ..interfaces import IExternalSourceManager
from ..errors import SourcePreviewError, SourceMissingError
from ..testing import FunctionalLayer


class DefaultCodeSourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_default_code_source_citation(self):
        """Test default code source implementation.
        """
        source = self.root._getOb('cs_citation')
        self.assertTrue(verifyObject(ICodeSource, source))
        self.assertTrue(verifyObject(IExternalSource, source))
        self.assertEqual(source.is_previewable(), True)
        self.assertEqual(source.is_usable(), True)
        self.assertNotEqual(source.get_fs_location(), None)
        self.assertNotEqual(source.get_parameters_form(), None)
        # The source is available
        self.assertItemsEqual(
            filter(lambda (name, candidate): name == source.id,
                   availableSources(self.root)),
            [(source.id, source)])

        # By default this source should work
        self.assertEqual(source.test_source(), None)

    def test_default_code_source_toc(self):
        """Test default code source implementation.
        """
        source = self.root._getOb('cs_toc')
        self.assertTrue(verifyObject(ICodeSource, source))
        self.assertTrue(verifyObject(IExternalSource, source))
        self.assertEqual(source.is_previewable(), True)
        self.assertEqual(source.is_usable(), True)
        self.assertNotEqual(source.get_fs_location(), None)
        self.assertNotEqual(source.get_parameters_form(), None)
        # The source is available
        self.assertItemsEqual(
            filter(lambda (name, candidate): name == source.id,
                   availableSources(self.root)),
            [(source.id, source)])

        # By default this source should work
        self.assertEqual(source.test_source(), None)

    def test_add_code_source(self):
        """Add a source, and verify its initial parameters.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource('codesource', 'A Code Source', 'script')

        source = self.root._getOb('codesource', None)
        self.assertTrue(verifyObject(ICodeSource, source))
        self.assertTrue(verifyObject(IExternalSource, source))

        # Add the rendering script
        factory = source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = source._getOb('script')
        script.write("""
##parameters=model,version,REQUEST

return "Render source"
""")

        # Now verify the source.
        self.assertEqual(source.is_usable(), True)
        self.assertEqual(source.is_previewable(), True)
        self.assertEqual(source.get_icon(), None)
        self.assertEqual(source.get_description(), '')
        self.assertEqual(source.test_source(), None)
        # An empty parameter form is created
        parameters = source.get_parameters_form()
        self.assertNotEqual(parameters, None)
        self.assertEqual(len(parameters.get_fields()), 0)
        # This code source was not created from the filesystem
        self.assertEqual(source.get_fs_location(), None)
        # The source is available
        self.assertItemsEqual(
            filter(lambda (name, candidate): name == source.id,
                   availableSources(self.root)),
            [(source.id, source)])


class CodeSourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

        # Create a test document.
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

        # Create a test code source.
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource('codesource', 'Test Source', 'script')
        source = self.root._getOb('codesource', None)

        # Add the rendering script
        factory = source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = source._getOb('script')
        script.write("""
##parameters=model,version,REQUEST

return "Render source"
""")

        # Create an instance of the code source
        version = self.root.example.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        controller = sources(TestRequest(), name='codesource')
        controller.create()
        self._instance = controller.getId()

    def get_controller(self):
        version = self.root.example.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        return sources(TestRequest(), instance=self._instance)

    def test_controller(self):
        """Test the controller for our source.
        """
        source = self.root.codesource
        controller = self.get_controller()
        self.assertTrue(verifyObject(IExternalSourceController, controller))

        self.assertEqual(controller.getSourceId(), source.id)
        self.assertEqual(controller.label, source.get_title())
        self.assertEqual(controller.description, source.get_description())
        self.assertEqual(controller.editable(), False)
        self.assertEqual(controller.render(), "Render source")

    def test_archive(self):
        """Test you can move the source in a folder. The rendering in
        the document will be broken after, and you will have a
        message, only in preview.
        """
        factory = self.root.manage_addProduct['OFSP']
        factory.manage_addFolder('folder', 'Folder')
        self.assertFalse(IFolder.providedBy(self.root.folder))
        self.assertNotIn('codesource', self.root.folder.objectIds())
        self.assertIn('codesource', self.root.objectIds())

        token = self.root.manage_cutObjects(['codesource'])
        self.root.folder.manage_pasteObjects(token)
        self.assertIn('codesource', self.root.folder.objectIds())
        self.assertNotIn('codesource', self.root.objectIds())

        controller = self.get_controller()
        self.assertTrue(verifyObject(IExternalSourceController, controller))
        with self.assertRaises(SourceMissingError) as error:
            controller.render()

        message = silvaviews.render(error.exception, TestRequest())
        self.assertEqual(message.strip(), '')
        message = silvaviews.render(
            error.exception, TestRequest(), preview=True)
        self.assertEqual(
            message.strip(),
            '<p>External Source unknown is not available.</p>')

        # The source is no longer available
        self.assertItemsEqual(
            filter(lambda (name, candidate): name == 'codesource',
                   availableSources(self.root)),
            [])

    def test_usable(self):
        """Test that switching to not usable remove the source from
        the available list.
        """
        source = self.root.codesource
        self.assertEqual(source.is_usable(), True)
        # The source is available
        self.assertItemsEqual(
            filter(lambda (name, candidate): name == source.id,
                   availableSources(self.root)),
            [(source.id, source)])

        source.set_usable(False)
        self.assertEqual(source.is_usable(), False)
        # The source is no longer available
        self.assertItemsEqual(
            filter(lambda (name, candidate): name == source.id,
                   availableSources(self.root)),
            [])

    def test_previewable(self):
        """Test that the preview prevent a source to be rendered if
        preview is asked.
        """
        source = self.root.codesource
        controller = self.get_controller()
        self.assertTrue(verifyObject(IExternalSourceController, controller))
        self.assertEqual(source.is_previewable(), True)
        self.assertEqual(controller.render(preview=True), "Render source")

        source.set_previewable(False)
        controller = self.get_controller()
        self.assertTrue(verifyObject(IExternalSourceController, controller))
        self.assertEqual(source.is_previewable(), False)
        with self.assertRaises(SourcePreviewError) as error:
            self.assertEqual(controller.render(preview=True))

        preview = silvaviews.render(error.exception, TestRequest())
        self.assertIsInstance(preview, basestring)
        self.assertIn('Test Source',  preview)
        self.assertNotEqual(preview, "Render source")
        # You can still render the not preview
        self.assertEqual(controller.render(), "Render source")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultCodeSourceTestCase))
    suite.addTest(unittest.makeSuite(CodeSourceTestCase))
    suite.addTest(doctest.DocTestSuite(
            'Products.SilvaExternalSources.codesources.youtube'))
    return suite
