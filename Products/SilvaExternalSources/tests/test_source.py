# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject

from ..interfaces import ICodeSource, IExternalSource
from ..testing import FunctionalLayer


class SourceTestCase(unittest.TestCase):
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
        self.assertEqual(source.test_source(), None)
        # An empty parameter form is created
        parameters = source.get_parameters_form()
        self.assertNotEqual(parameters, None)
        self.assertEqual(len(parameters.get_fields()), 0)
        # This code source was not created from the filesystem
        self.assertEqual(source.get_fs_location(), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SourceTestCase))
    return suite
