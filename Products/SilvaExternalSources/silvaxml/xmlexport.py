# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from five import grok
from zope.interface import Interface

from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.interfaces import ISilvaXMLExportFilter
from silva.core.interfaces import IVersion, ISilvaXMLProducer
from silva.core.xml import producers, NS_SILVA_URI
from silva.translations import translate as _
from zeam.component import getWrapper
from zeam.form.silva.interfaces import IXMLFormSerialization

from . import NS_SOURCE_URI
from ..interfaces import IExternalSourceManager
from ..interfaces import ISourceAsset, ISourceAssetVersion
from ..errors import SourceError
from .treehandler import ElementTreeContentHandler


logger = logging.getLogger('silva.core.xml')


class FieldProducer(ElementTreeContentHandler):

    def __init__(self, context, handler, **kwargs):
        ElementTreeContentHandler.__init__(self, **kwargs)
        self.context = context
        self.__handler = handler

    def getHandler(self):
        return self.__handler


class ExternalSourceExportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLProducer)
    grok.provides(ISilvaXMLExportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def prepare(self, name, text):
        self.sources = getWrapper(self.context, IExternalSourceManager)

    def __call__(self, tree):
        exported = self.handler.getExported()
        for node in tree.xpath(
                '//html:div[contains(@class, "external-source")]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            identifier = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']

            try:
                source = self.sources(exported.request, instance=identifier)
            except SourceError as error:
                exported.reportProblem(
                    u'Broken source in documen while exporting: {0}'.format(error),
                    self.context)
                continue
            if source.source is None:
                exported.reportProblem(
                    u"Broken source in document: source is gone in the export.",
                    self.context)
                continue
            node.attrib['source-identifier'] = source.getSourceId()

            # Fix this.
            producer = FieldProducer(self.context, self.handler, root=node)
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

    def sax_source_parameters(self, source_manager):
        """`source_manager` should be a IExternalSourceManager bounded to
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


class SourceAssetProducer(producers.SilvaVersionedContentProducer):
    grok.adapts(ISourceAsset, Interface)

    def sax(self):
        self.startElementNS(NS_SOURCE_URI, 'source-asset',
            {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(NS_SOURCE_URI, 'source-asset')


class SourceAssetVersionProducer(producers.SilvaProducer,
                                 SourceParametersProducer):
    grok.adapts(ISourceAssetVersion, Interface)

    def sax(self):
        manager = self.context.get_controller(self.getExported().request)
        self.startElementNS(
            NS_SILVA_URI,
            'content',
            {'version_id': self.context.id,
             'source-identifier': manager.getSourceId()})
        self.sax_metadata()
        self.sax_source_parameters(manager)
        self.endElementNS(NS_SILVA_URI, 'content')

