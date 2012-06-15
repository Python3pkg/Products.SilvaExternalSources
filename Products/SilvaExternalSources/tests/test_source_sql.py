
import unittest

from zope.interface.verify import verifyObject

from ..interfaces import IExternalSource
from ..testing import FunctionalLayer


class SQLSourceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_source(self):
        """Simply add and verify a SQL Source.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addSQLSource('sql_data', 'SQL Data')
        source = self.root._getOb('sql_data', None)
        self.assertNotEqual(source, None)
        self.assertTrue(verifyObject(IExternalSource, source))

    def test_render(self):
        assert False, 'TBD'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SQLSourceTestCase))
    return suite
