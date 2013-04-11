
import unittest
from lxml.etree import tostring, Element

from ..silvaxml.treehandler import ElementTreeContentHandler

NS_TEST1 = 'http://test.com/1'
NS_TEST2 = 'http://test.com/2'


class TreeHandlerTestCase(unittest.TestCase):

    def test_simple_node(self):
        handler = ElementTreeContentHandler()
        handler.startElement('test', {'id': 'value'})
        handler.characters('This is the content of test')
        handler.endElement('test')
        self.assertEqual(
            tostring(handler.etree),
            '<test id="value">This is the content of test</test>')

    def test_simple_node_with_default_namespace(self):
        handler = ElementTreeContentHandler()
        handler.startPrefixMapping(None, NS_TEST1)
        handler.startElement('test', {'id': 'value'})
        handler.characters('Content')
        handler.endElement('test')
        handler.endPrefixMapping(None)
        self.assertEqual(
            tostring(handler.etree),
            '<test xmlns="http://test.com/1" id="value">Content</test>')

    def test_two_node_with_default_namespace(self):
        handler = ElementTreeContentHandler()
        handler.startElement('container')
        handler.startPrefixMapping(None, NS_TEST1)
        handler.startElement('test', {'id': 'value'})
        handler.characters('Content')
        handler.endElement('test')
        handler.endPrefixMapping(None)
        handler.startPrefixMapping(None, NS_TEST1)
        handler.startElement('test', {'id': 'value'})
        handler.characters('Test')
        handler.endElement('test')
        handler.endPrefixMapping(None)
        handler.endElement('container')
        self.assertEqual(
            tostring(handler.etree),
            '<container>'
            '<test xmlns="http://test.com/1" id="value">Content</test>'
            '<test xmlns="http://test.com/1" id="value">Test</test>'
            '</container>')

    def test_two_node_with_default_namespace_on_root(self):
        root = Element('existing')
        handler = ElementTreeContentHandler(root=root)
        handler.startElement('container')
        handler.startPrefixMapping(None, NS_TEST1)
        handler.startElement('test', {'id': 'value'})
        handler.characters('Content')
        handler.endElement('test')
        handler.endPrefixMapping(None)
        handler.startPrefixMapping(None, NS_TEST1)
        handler.startElement('test', {'id': 'value'})
        handler.characters('Test')
        handler.endElement('test')
        handler.endPrefixMapping(None)
        handler.endElement('container')
        self.assertEqual(
            tostring(root),
            '<existing><container>'
            '<test xmlns="http://test.com/1" id="value">Content</test>'
            '<test xmlns="http://test.com/1" id="value">Test</test>'
            '</container></existing>')

    def test_two_node_with_two_default_namespace(self):
        handler = ElementTreeContentHandler()
        handler.startPrefixMapping(None, NS_TEST1)
        handler.startElement('root')
        for i in range(0, 2):
            handler.startElement('container')
            handler.startPrefixMapping(None, NS_TEST2)
            handler.startElement('test', {'id': 'value'})
            handler.characters('Content')
            handler.endElement('test')
            handler.endPrefixMapping(None)
            handler.startPrefixMapping(None, NS_TEST2)
            handler.startElement('test', {'id': 'value'})
            handler.characters('Test')
            handler.endElement('test')
            handler.endPrefixMapping(None)
            handler.endElement('container')
        handler.endElement('root')
        self.assertEqual(
            tostring(handler.etree),
            '<root xmlns="http://test.com/1">'
            '<container>'
            '<test xmlns="http://test.com/2" id="value">Content</test>'
            '<test xmlns="http://test.com/2" id="value">Test</test>'
            '</container>'
            '<container>'
            '<test xmlns="http://test.com/2" id="value">Content</test>'
            '<test xmlns="http://test.com/2" id="value">Test</test>'
            '</container>'
            '</root>')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TreeHandlerTestCase))
    return suite
