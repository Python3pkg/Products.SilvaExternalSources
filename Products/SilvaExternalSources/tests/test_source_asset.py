
import unittest

from zeam.component import getWrapper
from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import TestRequest
from silva.core.interfaces import IPublicationWorkflow

from ..testing import FunctionalLayer
from ..interfaces import ISourceAsset, ISourceAssetVersion
from ..interfaces import IExternalSourceManager


class SourceAssetTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_empty_source_asset(self):
        """Test an empty (aka broken) Source Asset.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addSourceAsset('asset', 'Test Asset')
        asset = self.root._getOb('asset', None)
        self.assertTrue(verifyObject(ISourceAsset, asset))
        version = asset.get_editable()
        self.assertTrue(verifyObject(ISourceAssetVersion, version))

        # A source asset can be used as a source, but does nothing
        self.assertEqual(asset.get_parameters_form(), None)
        self.assertEqual(asset.get_icon(), None)
        self.assertEqual(asset.get_description(), 'Broken or missing source.')
        self.assertEqual(asset.is_usable(), False)
        self.assertEqual(asset.is_previewable(), False)
        self.assertEqual(asset.is_cacheable(), False)

        # While rendering of the broken source asset, preview gives a
        # usefull message.
        with self.layer.get_browser(public_settings) as browser:
            browser.login('editor')
            self.assertEqual(browser.open('/root/++preview++/asset'), 200)
            self.assertEqual(browser.inspect.title, [])
            self.assertEqual(
                browser.inspect.content,
                ['External Source unknow is not available.'])

        # We published the asset and it stays not usuable.
        IPublicationWorkflow(asset).publish()
        self.assertEqual(asset.get_parameters_form(), None)
        self.assertEqual(asset.get_icon(), None)
        self.assertEqual(asset.get_description(), 'Broken or missing source.')
        self.assertEqual(asset.is_usable(), False)
        self.assertEqual(asset.is_previewable(), False)
        self.assertEqual(asset.is_cacheable(), False)
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/asset'), 200)
            self.assertEqual(browser.inspect.title, [])
            self.assertEqual(
                browser.inspect.content,
                ['Sorry, this Silva Source Asset is not viewable.'])

    def test_working_source_asset(self):
        """Test a working source asset.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addSourceAsset('asset', 'Test Asset')
        asset = self.root._getOb('asset', None)
        version = asset.get_editable()

        # Create a source with cs_citation
        sources = getWrapper(version, IExternalSourceManager)
        controller = sources(TestRequest(), name='cs_citation')
        controller.create()
        controller.getContent().citation = 'Silva is a great CMS.'
        version.set_parameters_identifier(controller.getId())

        # The content is not yet published.
        self.assertEqual(asset.get_parameters_form(), None)
        self.assertEqual(asset.get_icon(), None)
        self.assertEqual(asset.get_description(), 'Broken or missing source.')
        self.assertEqual(asset.is_usable(), False)
        self.assertEqual(asset.is_previewable(), False)
        self.assertEqual(asset.is_cacheable(), False)
        # You can preview it.
        with self.layer.get_browser(public_settings) as browser:
            browser.login('editor')
            self.assertEqual(browser.open('/root/++preview++/asset'), 200)
            self.assertEqual(browser.inspect.title, [])
            self.assertEqual(browser.inspect.content, ['Silva is a great CMS.'])

        # We publish it
        original = self.root.cs_citation
        IPublicationWorkflow(asset).publish()
        self.assertEqual(asset.get_parameters_form(), None)
        self.assertEqual(asset.get_icon(), original.get_icon())
        self.assertEqual(asset.get_description(), original.get_description())
        self.assertEqual(asset.is_usable(), True)
        self.assertEqual(asset.is_previewable(), True)
        self.assertEqual(asset.is_cacheable(), True)
        # Since it is published you can now see it.
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/asset'), 200)
            self.assertEqual(browser.inspect.title, [])
            self.assertEqual(browser.inspect.content, ['Silva is a great CMS.'])

    def test_broken_render_source_asset(self):
        """Test a source that renders a source with a broken render
        script.
        """
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addSourceAsset('asset', 'Test Asset')
        asset = self.root._getOb('asset', None)
        version = asset.get_editable()

        # Create a test code source
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource('brokensource', 'Broken Source', 'script')
        source = self.root._getOb('brokensource', None)

        # Add the rendering script
        factory = source.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = source._getOb('script')
        script.write("""
##parameters=model,version,REQUEST
I am broken
return "Render source"
""")

        # Create a source with the new test source
        sources = getWrapper(version, IExternalSourceManager)
        controller = sources(TestRequest(), name='brokensource')
        controller.create()
        version.set_parameters_identifier(controller.getId())

        # You can preview it, but it will fail with a nice message
        with self.layer.get_browser(public_settings) as browser:
            browser.login('editor')
            self.assertEqual(browser.open('/root/++preview++/asset'), 200)
            self.assertEqual(browser.inspect.title, [])
            self.assertEqual(
                browser.inspect.content,
                ['Error while rendering Broken Source\n  '
                 'A programmation error happened while rendering the source.'])

        IPublicationWorkflow(asset).publish()
        # We published the asset we still a nice error message instead
        # of a failure message.
        with self.layer.get_browser(public_settings) as browser:
            browser.options.handle_errors = False
            self.assertEqual(browser.open('/root/asset'), 200)
            self.assertEqual(browser.inspect.title, [])
            self.assertEqual(
                browser.inspect.content,
                ['Sorry, this Silva Source Asset is not viewable.'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SourceAssetTestCase))
    return suite
