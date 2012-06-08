# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from zope.interface import Interface

from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.interfaces import ISilvaXMLExportFilter
from silva.core.interfaces import IVersion, ISilvaXMLExportHandler
from zeam.component import getWrapper
from zeam.form.silva.interfaces import IXMLFormSerialization

from Products.Silva.silvaxml import xmlexport, NS_SILVA_URI
from Products.SilvaExternalSources.interfaces import IExternalSourceManager
from Products.SilvaExternalSources.silvaxml import NS_SOURCE_URI
from Products.SilvaExternalSources.silvaxml.treehandler import \
    ElementTreeContentHandler
from Products.SilvaExternalSources.SourceAsset import \
    SourceAsset, SourceAssetVersion


class FieldProducer(ElementTreeContentHandler):

    def __init__(self, handler, **kwargs):
        ElementTreeContentHandler.__init__(self, **kwargs)
        self.__handler = handler

    def getHandler(self):
       return self.__handler


xmlexport.theXMLExporter.registerNamespace(
    'silva-external-sources', NS_SOURCE_URI)


class ExternalSourceExportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLExportHandler)
    grok.provides(ISilvaXMLExportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def prepare(self, name, text):
        self.sources = getWrapper(self.context, IExternalSourceManager)

    def __call__(self, tree):
        request = self.handler.getInfo().request
        for node in tree.xpath(
                '//html:div[contains(@class, "external-source")]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            identifier = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']

            source = self.sources(request, instance=identifier)
            node.attrib['source-identifier'] = source.getSourceId()

            # Fix this.
            producer = FieldProducer(self.handler, root=node)
            producer.startPrefixMapping(None, NS_SOURCE_URI)
            producer.startElement('fields')
            for serializer in getWrapper(
                source, IXMLFormSerialization).getSerializers():
                producer.startElement(
                    'field', {(None, 'id'): serializer.identifier})
                serializer(producer)
                producer.endElement('field')
            producer.endElement('fields')


class SourceParametersProducer(object):
    """ A Mixin class for exporting a source parameters.
    """

    def getHandler(self):
        return self

    def source_parameters(self, source_manager):
        """`source_manager` should be a IExtenalSourceManager bounded to
        an instance.
        """
        self.startElementNS(NS_SOURCE_URI, 'fields')
        for serializer in getWrapper(
                source_manager, IXMLFormSerialization).getSerializers():
            self.startElementNS(
                NS_SOURCE_URI,
                'field',
                {(None, 'id'): serializer.identifier})
            serializer(self)
            self.endElementNS(NS_SOURCE_URI, 'field')
        self.endElementNS(NS_SOURCE_URI, 'fields')


class SourceAssetProducer(xmlexport.SilvaVersionedContentProducer):
    grok.adapts(SourceAsset, Interface)

    def sax(self):
        self.startElementNS(NS_SOURCE_URI, 'source-asset',
            {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_SOURCE_URI, 'source-asset')


class SourceAssetVersionProducer(xmlexport.SilvaBaseProducer,
                                 SourceParametersProducer):

    grok.adapts(SourceAssetVersion, Interface)

    def sax(self):
        source_manager = self.context.get_controller(self.getInfo().request)
        self.startElementNS(NS_SILVA_URI, 'content',
                            {'version_id': self.context.id,
                             'source-identifier': source_manager.getSourceId()})
        self.metadata()
        self.source_parameters(source_manager)
        self.endElementNS(NS_SILVA_URI, 'content')

