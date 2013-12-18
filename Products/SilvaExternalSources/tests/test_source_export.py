
import unittest
import tempfile
import shutil
import os

from ..testing import FunctionalLayer
from ..CodeSourceService import CodeSourceInstallable
from ..CodeSourceService import CodeSourceExportable, InstallationError

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

TEST_SCRIPT = """## Script (Python) "%s"
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
        script.write(TEST_SCRIPT % 'script')

        installable = CodeSourceInstallable('test:', self.directory)
        installable.export(self.root.source)

        self.assertItemsEqual(
            os.listdir(self.directory),
            ['parameters.xml', 'script.py', 'source.ini'])
        self.assertIsFile('script.py')
        self.assertIsFile('source.ini')
        self.assertIsFile('parameters.xml')
        with open(self.get_path('script.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT % 'script')
        with open(self.get_path('source.ini'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SOURCE)

    def test_python_script_with_extension(self):
        """Test export a code source with a script with an extension.
        """
        # Add the rendering script
        factory = self.root.source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script.xml')
        script = self.root.source._getOb('script.xml')
        script.write(TEST_SCRIPT % 'script.xml')

        installable = CodeSourceInstallable('test:', self.directory)
        installable.export(self.root.source)

        self.assertItemsEqual(
            os.listdir(self.directory),
            ['parameters.xml', 'script.xml.py', 'source.ini'])
        self.assertIsFile('script.xml.py')
        self.assertIsFile('source.ini')
        self.assertIsFile('parameters.xml')
        with open(self.get_path('script.xml.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT % 'script.xml')
        with open(self.get_path('source.ini'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SOURCE)

    def test_dtml_document(self):
        """Test export a code source with a DTML document with an invalid
        installable.

        """
        # Add the rendering script
        factory = self.root.source.manage_addProduct['OFS']
        factory.manage_addDTMLDocument('cool.css', 'Cool CSS')
        css = self.root.source._getOb('cool.css')
        css.munge(TEST_DTML)

        # Locations doesn't match, so the export fails.
        installable = CodeSourceInstallable('other:', '/')
        with self.assertRaises(InstallationError):
            installable.export(self.root.source)

        # Nothing got exported.
        self.assertItemsEqual(os.listdir(self.directory), [])

        # With an explicit location it will work, and not touch the installable.
        installable.export(self.root.source, directory=self.directory)

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
        """Test export a code source via a not valid installable with a
        folder.
        """
        factory = self.root.source.manage_addProduct['OFS']
        factory.manage_addFolder('helpers')
        factory = self.root.source.helpers.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source.helpers._getOb('script')
        script.write(TEST_SCRIPT % "script")
        # Add the rendering script
        factory = self.root.source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source._getOb('script')
        script.write(TEST_SCRIPT % "script")

        installable = CodeSourceInstallable('test:', self.directory)
        self.assertFalse(installable.validate())
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
            self.assertEqual(script.read(), TEST_SCRIPT % "script")
        with open(self.get_path('helpers', 'script.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT % "script")

    def test_folder_export_only(self):
        """Test export only a code source containing a folder without using a
        full installable.
        """
        factory = self.root.source.manage_addProduct['OFS']
        factory.manage_addFolder('helpers')
        factory = self.root.source.helpers.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source.helpers._getOb('script')
        script.write(TEST_SCRIPT % "script")
        # Add the rendering script
        factory = self.root.source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.source._getOb('script')
        script.write(TEST_SCRIPT % "script")

        CodeSourceExportable().export(self.root.source, self.directory)

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
            self.assertEqual(script.read(), TEST_SCRIPT % "script")
        with open(self.get_path('helpers', 'script.py'), 'rb') as script:
            self.assertEqual(script.read(), TEST_SCRIPT % "script")



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeSourceExportTestCase))
    return suite
