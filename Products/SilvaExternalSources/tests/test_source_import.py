
import unittest
import shutil
import tempfile
import os

from zope.interface.verify import verifyObject

from ..interfaces import ICodeSource
from ..testing import FunctionalLayer
from ..CodeSourceService import CodeSourceInstallable, InstallationError


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

    def test_import(self):
        installable = CodeSourceInstallable('test:', self.get_path())
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

    def test_import_already_exist(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('cs_fancytest', 'Fancy duplicate')

        installable = CodeSourceInstallable('test:', self.get_path())
        # The identifier is already in use, so you get an error.
        with self.assertRaises(InstallationError):
            installable.install(self.root)

    def test_import_export_and_update(self):
        installable = CodeSourceInstallable(
            'test:', self.get_path())
        # Return True upon success
        self.assertTrue(installable.install(self.root))

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

        # Call again install and it will return False, before it is
        # already installed.
        self.assertFalse(installable.install(self.root))

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
        self.assertTrue(installable.update(source, purge=True))
        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'README', 'script'])
        self.assertItemsEqual(
            source.css.objectIds(),
            ['advanced.css'])
        self.assertItemsEqual(
            source.js.objectIds(),
            ['advanced.js'])

    def test_rename_file_and_update(self):
        installable = CodeSourceInstallable('test:', self.get_path())
        self.assertTrue(installable.install(self.root))
        source = self.root._getOb('cs_fancytest', None)
        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'README', 'script'])

        os.rename(
            self.get_path('README.txt'),
            self.get_path('RENAMED_README.txt'))
        self.assertTrue(installable.update(source, purge=True))
        self.assertItemsEqual(
            source.objectIds(),
            ['css', 'feedback', 'js', 'RENAMED_README', 'script'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceImportTestCase))
    return suite
