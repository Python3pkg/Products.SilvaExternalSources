# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject

from Products.SilvaExternalSources.interfaces import ICodeSource
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.testing import FunctionalLayer


class SourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_code_source(self):
        """Test default code source implementation.
        """
        source = self.root.cs_citation
        self.assertTrue(verifyObject(ICodeSource, source))
        self.assertTrue(verifyObject(IExternalSource, source))

        # By default this source should work
        self.assertEqual(source.test_source(), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SourceTestCase))
    return suite
