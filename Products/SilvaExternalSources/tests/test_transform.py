# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import TestRequest, tests
from zope.component import getMultiAdapter
from zope.interface.verify import verifyObject
from zeam.component import getWrapper

from silva.core.editor.transform.interfaces import ITransformerFactory
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.views.interfaces import IPreviewLayer

from ..interfaces import IExternalSourceManager, IExternalSourceInstance
from ..testing import FunctionalLayer


class SourceTransformerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        # Create a test document.
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Document Example')


class CreateSourceTransformerTestCase(SourceTransformerTestCase):


    def transform(self, text, filter, version, public=True):
        """Helper to call transform.
        """
        layers = []
        if not public:
            layers = [IPreviewLayer]
        request = TestRequest(layers=layers)
        factory = getMultiAdapter((version, request), ITransformerFactory)
        transformer = factory('body', version.body, text, filter)
        return unicode(transformer)

    def test_create_source(self):
        """Create a source using the transformer.
        """
        version = self.root.document.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 0)

        # We now save the source, this going to create it.
        saved_text = self.transform("""
<h1>
   Document Example
</h1>
<div class="external-source"
     data-silva-name="cs_citation"
     data-silva-settings="field_citation=Super%20citation&field_author=moi">
</div>
""", ISaveEditorFilter, version)

        # One source have been created.
        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 1)
        instance_key = list(sources.all())[0]
        parameters, source = sources.get_parameters(instance=instance_key)
        self.assertTrue(verifyObject(IExternalSourceInstance, parameters))
        self.assertEqual(parameters.get_source_identifier(), 'cs_citation')
        self.assertEqual(parameters.get_parameter_identifier(), instance_key)
        self.assertEqual(source.id, 'cs_citation')
        self.assertEqual(parameters.citation, u'Super citation')
        self.assertEqual(parameters.author, u'moi')
        self.assertEqual(parameters.source, u'')
        tests.assertXMLEqual(
            saved_text,
            """
<div class="external-source" data-source-instance="%s">
</div>
""" % instance_key)

        # You can render this source for the editor
        editor_text = self.transform(saved_text, IInputEditorFilter, version)
        tests.assertXMLEqual(
            editor_text, """
<h1>
   Document Example
</h1>
<div class="external-source" data-silva-instance="%s">
</div>
""" % instance_key)

        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 1)



class EditSourceTransformerTestCase(SourceTransformerTestCase):

    def setUp(self):
        super(EditSourceTransformerTestCase, self).setUp()
        version = self.root.document.get_editable()
        sources = getWrapper(version, IExternalSourceManager)
        controller = sources(TestRequest(form={
                    'field_citation': "Don't trust citations on the Internet",
                    'field_author': "Charlemagne",
                    'field_source': "The Internet"}), name='cs_citation')
        controller.create()
        self.instance_key = controller.getId()
        self.saved_text = """
<div class="external-source" data-source-instance="%s">
</div>
""" % self.instance_key

    def test_display_source(self):
        """If you render without any layer, you will see the code
        source rendered.
        """
        version = self.root.document.get_editable()
        factory = getMultiAdapter(
            (version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'body', version.body, self.saved_text, IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
"""
<div class="external-source">
 <div class="citation">
  Don't trust citations on the Internet
  <div class="author">
   Charlemagne
  </div>
  <div class="source">
   The Internet
  </div>
 </div>
</div>
""")

        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 1)

    def test_display_broken_source_preview(self):
        """If you delete the code source object, and render with a
        preview layer, you have an error message.
        """
        self.root.manage_delObjects(['cs_citation'])

        version = self.root.document.get_editable()
        factory = getMultiAdapter(
            (version, TestRequest(layers=[IPreviewLayer])),
            ITransformerFactory)
        transformer = factory(
            'body', version.body, self.saved_text, IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
"""
<div class="external-source broken-source">
 <p>
   External Source unknown is not available.
 </p>
</div>
""")

        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 1)

    def test_display_broken_source_public(self):
        """If you delete the code source object, and render without a
        preview layer, you have no message.
        """
        self.root.manage_delObjects(['cs_citation'])

        version = self.root.document.get_editable()
        factory = getMultiAdapter(
            (version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body', version.body, self.saved_text, IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
"""
<div class="external-source">
</div>
""")

        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 1)

    def test_delete_source(self):
        """If you save again without provided the html for the source,
        it is removed.
        """
        version = self.root.document.get_editable()
        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory('body', version.body, "", ISaveEditorFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            "")

        sources = getWrapper(version, IExternalSourceManager)
        self.assertEqual(len(sources.all()), 0)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CreateSourceTransformerTestCase))
    suite.addTest(unittest.makeSuite(EditSourceTransformerTestCase))
    return suite

