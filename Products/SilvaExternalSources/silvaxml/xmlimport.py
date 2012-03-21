# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok

from silva.core.interfaces import IVersion, ISilvaXMLImportHandler
from silva.core.editor.transform.interfaces import ISilvaXMLImportFilter
from silva.core.editor.transform.base import TransformationFilter
from zeam.component import getWrapper
from zeam.form.silva.interfaces import IXMLFormSerialization

from Products.SilvaExternalSources.silvaxml import NS_SOURCE_URI
from Products.SilvaExternalSources.interfaces import IExternalSourceManager
from Products.SilvaExternalSources.interfaces import SourceError

logger = logging.getLogger('silva.xml')


class ExternalSourceImportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLImportHandler)
    grok.provides(ISilvaXMLImportFilter)
    grok.order(15)

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
            name = node.attrib['source-identifier']
            try:
                source = self.sources(request, name=name)
            except SourceError:
                logger.warn(
                    u"unknown external source %r in import", name)
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


