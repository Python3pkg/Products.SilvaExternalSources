# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.interfaces import IVersion, ISilvaXMLExportHandler
from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.interfaces import ISilvaXMLExportFilter
from Products.Silva.silvaxml import xmlexport
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances
from Products.SilvaExternalSources.silvaxml import NS_SOURCE_URI
from Products.SilvaExternalSources.silvaxml.treehandler import \
    ElementTreeContentHandler


class FieldProducer(ElementTreeContentHandler):

    def __init__(self, handler, **kwargs):
        ElementTreeContentHandler.__init__(self, **kwargs)
        self.__handler = handler

    def getHandler(self):
       return self.__handler


xmlexport.theXMLExporter.registerNamespace('silva-external-sources', NS_SOURCE_URI)


class ExternalSourceExportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLExportHandler)
    grok.provides(ISilvaXMLExportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)

    def __call__(self, tree):
        request = self.handler.getInfo().request
        for node in tree.xpath(
                '//html:div[contains(@class, "external-source")]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            identifier = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']
            instance = self.sources.bind(identifier, self.context, request)
            source, form = instance.get_source_and_form()
            node.attrib['source-identifier'] = source.getId()

            producer = FieldProducer(self.handler, root=node)
            producer.startPrefixMapping(None, NS_SOURCE_URI)
            producer.startElement('fields')
            for field in form.fields(ignore_content=False):
                producer.startElement('field', {(None, 'id'): field.id})
                field.serialize(producer)
                producer.endElement('field')
            producer.endElement('fields')


