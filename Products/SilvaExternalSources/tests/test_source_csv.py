
import unittest

from zope.interface.verify import verifyObject
from Products.Silva.testing import TestRequest, assertTriggersEvents
from Products.Silva.tests.helpers import open_test_file

from ..interfaces import ICSVSource, IExternalSource
from ..testing import FunctionalLayer


class CSVSourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCSVSource('csv_data', 'CSV Data')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

    def test_source(self):
        """Simply add and verify a CSV Source.
        """
        source = self.root._getOb('csv_data', None)
        self.assertNotEqual(source, None)
        self.assertTrue(verifyObject(ICSVSource, source))
        self.assertTrue(ICSVSource.extends(IExternalSource))
        self.assertItemsEqual(source.objectIds(), ['layout'])
        self.assertEqual(source.is_previewable(), True)
        self.assertEqual(source.is_usable(), True)
        self.assertEqual(source.get_file_size(), 0)
        self.assertEqual(source.get_filename(), 'csv_data.csv')
        self.assertEqual(source.get_mime_type(), 'text/csv')

        with open_test_file('informations.csv', globals()) as data:
            with assertTriggersEvents('ObjectModifiedEvent'):
                source.set_file(data)

        self.assertEqual(source.get_file_size(), 281)
        self.assertEqual(source.get_filename(), 'csv_data.csv')
        self.assertEqual(source.get_mime_type(), 'text/csv')

    def test_render(self):
        """Test rendering the CSV source.
        """
        source = self.root._getOb('csv_data', None)
        version = self.root.example.get_editable()
        with open_test_file('informations.csv', globals()) as data:
            source.set_file(data)

        rendered = source.to_html(version, TestRequest())
        self.assertNotEqual(rendered, '')
        self.assertIn('Update CSV tests', rendered)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CSVSourceTestCase))
    return suite
