
import unittest
import shutil
import tempfile
import os

from zope.interface.verify import verifyObject

from ..interfaces import ICodeSource
from ..testing import FunctionalLayer
from ..CodeSourceService import CodeSourceInstallable


class CodeSourceImportTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        self.directory = tempfile.mkdtemp('tests')
        shutil.copytree(
            self.layer.get_fixture('cs_fancytest'),
            os.path.join(self.directory, 'cs_fancytest'))
        with open(self.get_path('.DS_Store'), 'wb') as test:
            test.write('test')
        with open(self.get_path('._source.ini'), 'wb') as test:
            test.write('test')

    def tearDown(self):
        shutil.rmtree(self.directory)

    def get_path(self, *names):
        return os.path.join(self.directory, 'cs_fancytest', *names)

    def test_fancy(self):
        installable = CodeSourceInstallable(
            'test:', self.get_path(), os.listdir(self.get_path()))
        installable.install(self.root)

        source = self.root._getOb('cs_fancytest', None)
        self.assertTrue(verifyObject(ICodeSource, source))
        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'README', 'script'])
        self.assertItemsEqual(
            source.css.objectIds(),
            ['advanced.css'])
        self.assertItemsEqual(
            source.js.objectIds(),
            ['advanced.js'])

    def test_import_and_export_fancy(self):
        installable = CodeSourceInstallable(
            'test:', self.get_path(), os.listdir(self.get_path()))
        installable.install(self.root)

        source = self.root._getOb('cs_fancytest', None)
        self.assertTrue(verifyObject(ICodeSource, source))
        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'README', 'script'])
        self.assertItemsEqual(
            source.css.objectIds(),
            ['advanced.css'])
        self.assertItemsEqual(
            source.js.objectIds(),
            ['advanced.js'])

        # We export again the source.
        installable.export(source)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceImportTestCase))
    return suite
