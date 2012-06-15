
import unittest

from zope.interface.verify import verifyObject

from ..interfaces import ICSVSource, IExternalSource
from ..testing import FunctionalLayer


class CSVSourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def test_source(self):
        """Simply add and verify a CSV Source.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCSVSource('csv_data', 'CSV Data')
        source = self.root._getOb('csv_data', None)
        self.assertNotEqual(source, None)
        self.assertTrue(verifyObject(ICSVSource, source))
        self.assertTrue(ICSVSource.extends(IExternalSource))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CSVSourceTestCase))
    return suite
