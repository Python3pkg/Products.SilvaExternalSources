
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
            'test:', self.get_path())
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

    def test_import_export_and_update_fancy(self):
        installable = CodeSourceInstallable(
            'test:', self.get_path())
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
        self.assertItemsEqual(
            os.listdir(self.get_path()),
            ['css', 'feedback.xml', 'js', 'parameters.xml',
             'README.txt', 'script.pt', 'source.ini'])
        self.assertItemsEqual(
            os.listdir(self.get_path('css')),
            ['advanced.css.dtml'])
        self.assertItemsEqual(
            os.listdir(self.get_path('js')),
            ['advanced.js'])

        # And update it
        installable.update(source, purge=True)
        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'README', 'script'])
        self.assertItemsEqual(
            source.css.objectIds(),
            ['advanced.css'])
        self.assertItemsEqual(
            source.js.objectIds(),
            ['advanced.js'])

    def test_rename_and_update(self):
        installable = CodeSourceInstallable(
            'test:', self.get_path())
        installable.install(self.root)

        old_filename = self.get_path('README.txt')
        new_filename = self.get_path('RENAMED_README.txt')

        os.rename(old_filename, new_filename)

        source = self.root._getOb('cs_fancytest', None)

        try:
            installable.update(source, purge=True)
        except(IOError):
            self.fail('''The code source cannot be updated because one
                      of its file has been renamed on the file system.''')

        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'RENAMED_README', 'script'])

        os.rename(new_filename, old_filename)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceImportTestCase))
    return suite
