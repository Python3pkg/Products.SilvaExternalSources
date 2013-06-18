
import unittest
import tempfile
import shutil
import os

from ..testing import FunctionalLayer
from ..CodeSourceService import CodeSourceInstallable

TEST_DTML = """body { color: red };
"""

TEST_SOURCE = """[source]
id = source
title = Test Source
render_id = script
usuable = yes
previewable = yes
cacheable = no

"""

TEST_SCRIPT = """## Script (Python) "script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model,version,REQUEST
##title=
##
return "Render source"
"""

class CodeSourceExportTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        self.directory = tempfile.mkdtemp('tests')
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource('source', 'Test Source', 'script')
        self.root.source._fs_location = 'test:'

    def tearDown(self):
        shutil.rmtree(self.directory)

    def assertIsFile(self, *names):
        self.assertTrue(os.path.isfile(self.get_path(*names)))

    def assertIsDirectory(self, *names):
        self.assertTrue(os.path.isdir(self.get_path(*names)))

    def get_path(self, *names):
        return os.path.join(self.directory, *names)

    def test_python_script(self):
        """Test export a code source with a script.
        """
        # Add the rendering script
        factory = self.root.source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source._getOb('script')
        script.write(TEST_SCRIPT)

        installable = CodeSourceInstallable('test:', self.directory, [])
        installable.export(self.root.source)

        self.assertItemsEqual(
            os.listdir(self.directory),
            ['parameters.xml', 'script.py', 'source.ini'])
        self.assertIsFile('script.py')
        self.assertIsFile('source.ini')
        self.assertIsFile('parameters.xml')
        with open(self.get_path('script.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT)
        with open(self.get_path('source.ini'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SOURCE)

    def test_dtml_document(self):
        """Test export a code source with a DTML document.
        """
        # Add the rendering script
        factory = self.root.source.manage_addProduct['OFS']
        factory.manage_addDTMLDocument('cool.css', 'Cool CSS')
        css = self.root.source._getOb('cool.css')
        css.munge(TEST_DTML)

        installable = CodeSourceInstallable('test:', self.directory, [])
        installable.export(self.root.source)

        self.assertItemsEqual(
            os.listdir(self.directory),
            ['parameters.xml', 'cool.css.dtml', 'source.ini'])
        self.assertIsFile('cool.css.dtml')
        self.assertIsFile('source.ini')
        self.assertIsFile('parameters.xml')
        with open(self.get_path('cool.css.dtml'), 'rb') as script:
            self.assertEqual(script.read(), TEST_DTML)
        with open(self.get_path('source.ini'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SOURCE)

    def test_folder(self):
        """Test export a code source with a folder.
        """
        factory = self.root.source.manage_addProduct['OFS']
        factory.manage_addFolder('helpers')
        factory = self.root.source.helpers.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source.helpers._getOb('script')
        script.write(TEST_SCRIPT)
        # Add the rendering script
        factory = self.root.source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source._getOb('script')
        script.write(TEST_SCRIPT)

        installable = CodeSourceInstallable('test:', self.directory, [])
        installable.export(self.root.source)

        self.assertItemsEqual(
            os.listdir(self.directory),
            ['parameters.xml', 'script.py', 'helpers', 'source.ini'])
        self.assertIsDirectory('helpers')
        self.assertIsFile('helpers', 'script.py')
        self.assertIsFile('script.py')
        self.assertIsFile('source.ini')
        self.assertIsFile('parameters.xml')
        with open(self.get_path('source.ini'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SOURCE)
        with open(self.get_path('script.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT)
        with open(self.get_path('helpers', 'script.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceExportTestCase))
    return suite
