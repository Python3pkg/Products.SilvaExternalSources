# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok
from zope.component import getMultiAdapter

from silva.core.interfaces import IVersion, ISilvaXMLImportHandler
from silva.core.editor.transform.interfaces import ISilvaXMLImportFilter
from silva.core.editor.transform.base import TransformationFilter

from Products.Formulator.interfaces import IFieldValueWriter
from Products.SilvaExternalSources.silvaxml import NS_URI
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances

logger = logging.getLogger('silva.xml')


class ExternalSourceImportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLImportHandler)
    grok.provides(ISilvaXMLImportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)
        self.request = self.handler.getInfo().request

    def __call__(self, tree):
        for source_node in tree.xpath(
                '//html:div[contains(@class, "external-source")]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            identifier = self.sources.new(
                source_node.attrib['source-identifier'])
            instance = self.sources.bind(
                identifier, self.context, self.request)
            source, form = instance.get_source_and_form()
            fields_by_id = dict([(f.id, f) for f in form.fields()])
            for field_node in source_node.xpath(
                    './cs:fields/cs:field', namespaces={'cs': NS_URI}):
                field_id = field_node.attrib['id']
                field = fields_by_id.get(field_id)
                if field is None:
                    logger.warn(u"unknown external source parameter %s in %s" % (
                            field_id, source_node.attrib['source-identifier']))
                    # This field have been removed. Ignore it.
                    continue
                # The value is composed of sub-tags
                value = field.deserialize(field_node, self.handler)
                writer = getMultiAdapter(
                    (field._field, form), IFieldValueWriter)
                writer(value)

            del source_node[:]
            del source_node.attrib['source-identifier']
            source_node.attrib['data-source-instance'] = identifier


