# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from lxml import etree
from lxml.sax import SaxError, _getNsTag
from xml.sax.handler import ContentHandler


class ElementTreeContentHandler(ContentHandler):
    """Build an lxml ElementTree from SAX-like events. This is a
    simplified version of lxml.sax.ElementTreeContentHandler that
    behave in a compatible fashion with Sprout version.
    """
    def __init__(self, makeelement=None, root=None):
        self._root = root
        self._element_stack = []
        if self._root is not None:
            self._element_stack.append(self._root)
        self._default_ns = None
        self._ns_mapping = {None: [None]}
        self._new_mappings = {}
        if makeelement is None:
            makeelement = etree.Element
        self._makeelement = makeelement

    @property
    def etree(self):
        "Contains the generated ElementTree after parsing is finished."
        return etree.ElementTree(self._root)

    def setDocumentLocator(self, locator):
        pass

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startPrefixMapping(self, prefix, uri):
        self._new_mappings[prefix] = uri
        try:
            self._ns_mapping[prefix].append(uri)
        except KeyError:
            self._ns_mapping[prefix] = [uri]
        if prefix is None:
            self._default_ns = uri

    def endPrefixMapping(self, prefix):
        ns_uri_list = self._ns_mapping[prefix]
        ns_uri_list.pop()
        if prefix is None:
            self._default_ns = ns_uri_list[-1]

    def startElementNS(self, ns_name, qname, attributes=None):
        ns_uri, local_name = ns_name
        if ns_uri:
            el_name = "{%s}%s" % ns_name
        elif self._default_ns:
            el_name = "{%s}%s" % (self._default_ns, local_name)
        else:
            el_name = local_name

        if attributes:
            attrs = {}
            for name_tuple, value in attributes.iteritems():
                if isinstance(name_tuple, basestring):
                    attr_name = name_tuple
                elif name_tuple[0]:
                    attr_name = "{%s}%s" % name_tuple
                else:
                    attr_name = name_tuple[1]
                attrs[attr_name] = value
        else:
            attrs = None

        element_stack = self._element_stack
        if self._root is None:
            element = self._root = self._makeelement(
                el_name, attrs, self._new_mappings)
        else:
            element = etree.SubElement(
                element_stack[-1], el_name, attrs, self._new_mappings)
        element_stack.append(element)
        self._new_mappings.clear()

    def processingInstruction(self, target, data):
        pass

    def endElementNS(self, ns_name, qname):
        element = self._element_stack.pop()
        ns_uri, name = ns_name
        if ns_uri is None:
            ns_uri = self._default_ns
        if (ns_uri, name) != _getNsTag(element.tag):
            raise SaxError("Unexpected element closed: {%s}%s" % ns_name)

    def startElement(self, name, attributes=None):
        self.startElementNS((None, name), name, attributes)

    def endElement(self, name):
        self.endElementNS((None, name), name)

    def characters(self, data):
        last_element = self._element_stack[-1]
        try:
            # if there already is a child element, we must append to its tail
            last_element = last_element[-1]
            last_element.tail = (last_element.tail or '') + data
        except IndexError:
            # otherwise: append to the text
            last_element.text = (last_element.text or '') + data

    ignorableWhitespace = characters
