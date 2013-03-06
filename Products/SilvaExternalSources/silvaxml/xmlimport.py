# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import lxml.sax

from five import grok

from silva.core import conf as silvaconf
from silva.core.interfaces import IVersion, ISilvaXMLHandler
from silva.core.editor.transform.interfaces import ISilvaXMLImportFilter
from silva.core.editor.transform.base import TransformationFilter
from silva.core.xml import handlers
from zeam.component import getWrapper
from zeam.form.silva.interfaces import IXMLFormSerialization

from silva.core.xml import NS_SILVA_URI

from . import NS_SOURCE_URI
from ..interfaces import IExternalSourceManager
from ..errors import SourceError

logger = logging.getLogger('silva.core.xml')

silvaconf.namespace(NS_SOURCE_URI)


class ExternalSourceImportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLHandler)
    grok.provides(ISilvaXMLImportFilter)
    grok.order(15)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def prepare(self, name, text):
        self.sources = getWrapper(self.context, IExternalSourceManager)

    def __call__(self, tree):
        importer = self.handler.getExtra()
        request = importer.request
        for node in tree.xpath(
                '//html:div[contains(@class, "external-source")]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            name = node.attrib.get('source-identifier')
            if name is None:
                importer.reportProblem(
                    u"Broken external source in import.", self.context)
                continue
            try:
                source = self.sources(request, name=name)
            except SourceError as error:
                importer.reportProblem(
                    u"Broken source in import: {0}".format(error),
                    self.context)
                continue
            identifier = source.new()

            deserializers = getWrapper(
                source, IXMLFormSerialization).getDeserializers()
            for field_node in node.xpath(
                './cs:fields/cs:field', namespaces={'cs': NS_SOURCE_URI}):
                field_id = field_node.attrib['id']
                if field_id.startswith('field-'):
                    # XXX Backward compatiblity 3.0b1
                    field_id = field_id[6:].replace('-', '_')
                deserializer = deserializers.get(field_id)
                if deserializer is None:
                    # This field have been removed. Ignore it.
                    logger.warn(
                        u"unknown external source parameter %s in %s" % (
                            field_id, node.attrib['source-identifier']))
                    continue
                # Deserialize the value
                deserializer(field_node, self.handler)

            del node[:]
            del node.attrib['source-identifier']
            node.attrib['data-source-instance'] = identifier


class SourceParameterHandler(handlers.SilvaHandler):
    """ Handle source parameter.

    Only to be used by a SourceParametersHandler
    """

    proxy = None
    field_id = None

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SOURCE_URI, 'field'):
            self.proxy = lxml.sax.ElementTreeContentHandler()
            self.proxy.startElementNS(name, qname, attrs)
            self.field_id = attrs[(None, 'id')]
        elif self.proxy is not None:
            self.proxy.startElementNS(name, qname, attrs)

    def characters(self, input_text):
        text = input_text.strip()
        if self.proxy is not None and text:
            self.proxy.characters(text)

    def endElementNS(self, name, qname):
        if name == (NS_SOURCE_URI, 'field'):
            self.proxy.endElementNS(name, qname)
            deserializer = self.parentHandler().deserializers[self.field_id]
            deserializer(self.proxy.etree.getroot(), self.parentHandler())
            del self.proxy
        elif self.proxy is not None:
            self.proxy.endElementNS(name, qname)


class SourceParametersHandler(handlers.SilvaHandler):
    """Handler for importing source parameters.

    The parent handler must define a `source` property
    (IExternalSourceManager) to be used by this handler.

    see SourceAssetVersionHandler for example usage.
    """
    deserializers = None

    def getOverrides(self):
        return {(NS_SOURCE_URI, 'field'): SourceParameterHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SOURCE_URI, 'fields'):
            self.deserializers = getWrapper(
                self.parentHandler().source,
                IXMLFormSerialization).getDeserializers()

    def endElementNS(self, name, qname):
        if name == (NS_SOURCE_URI, 'fields'):
            del self.deserializers


class SourceAssetVersionHandler(handlers.SilvaVersionHandler):
    source = None

    def getOverrides(self):
        return {(NS_SOURCE_URI, 'fields'): SourceParametersHandler}

    def startElementNS(self, name, qname, attrs):
        if (NS_SILVA_URI, 'content') == name:
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['SilvaExternalSources']
            factory.manage_addSourceAssetVersion(uid, '')
            self.setResultId(uid)
            source_identifier = attrs[(None, 'source-identifier')]
            factory = getWrapper(self.result(), IExternalSourceManager)
            self.source = factory(self.getExtra().request,
                                  name=source_identifier)
            identifier = self.source.new()
            self.result().set_parameters_identifier(identifier)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if (NS_SILVA_URI, 'content') == name:
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()
            self.source_manager = None


class SourceAssetHandler(handlers.SilvaHandler):
    silvaconf.name('source-asset')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): SourceAssetVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SOURCE_URI, 'source-asset'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['SilvaExternalSources']
            factory.manage_addSourceAsset(identifier, '', no_default_version=True)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SOURCE_URI, 'source-asset'):
            self.notifyImport()
