# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject

from Products.Silva.testing import TestRequest
from Products.ZSQLMethods.tests.dummy import DummySQLConnection
from Shared.DC.ZRDB.DA import DatabaseError

from ..interfaces import IExternalSource
from ..testing import FunctionalLayer


class SQLSourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        factory = self.root.manage_addProduct['ZSQLiteDA']
        factory.manage_addZSQLiteConnection('sqlite', 'SQLite', ':memory:')
        self.root._setObject('dummy', DummySQLConnection('dummy', 'Dummy'))

    def test_source(self):
        """Simply add and verify a SQL Source.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addSQLSource('sql_data', 'SQL Data')
        source = self.root._getOb('sql_data', None)
        self.assertNotEqual(source, None)
        self.assertTrue(verifyObject(IExternalSource, source))
        self.assertItemsEqual(source.objectIds(), ['layout'])
        self.assertEqual(source.is_previewable(), True)
        self.assertEqual(source.is_usable(), True)
        self.assertItemsEqual(
            source.available_connection_ids(),
            [('Dummy (dummy)', 'dummy'),
             ('SQLite (sqlite), which is <font color=red> not connected</font>', 'sqlite')])

    def test_render(self):
        """Test rendering of the sql source.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addSQLSource('sql_data', 'SQL Data')

        source = self.root._getOb('sql_data', None)
        source._set_connection_id('dummy')
        version = self.root.example.get_editable()

        # The dummy connector is not connected
        with self.assertRaises(DatabaseError):
            source.to_html(version, TestRequest())

        # XXX write test with a DB.

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SQLSourceTestCase))
    return suite
