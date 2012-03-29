# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml.html

from five import grok
from zeam.component import getComponent
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest

from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.editor.output import clean_editor_attributes
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter

from Products.SilvaExternalSources.interfaces import IExternalSourceManager
from Products.SilvaExternalSources.interfaces import ISourceEditableVersion
from Products.SilvaExternalSources.interfaces import SourceError
from Products.SilvaExternalSources.editor.utils import parse_qs


SOURCE_XPATH = '//div[contains(@class, "external-source")]'

def broken_source(msg):
    return '<div class="broken-source">%s</div>' % str(msg)


class ExternalSourceSaveFilter(TransformationFilter):
    """Process External Source information on save.
    """
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)
    grok.order(20)
    grok.adapts(ISourceEditableVersion, IBrowserRequest)

    def prepare(self, name, text):
        self.sources = getComponent(
            self.context, IExternalSourceManager)(self.context)
        self.seen = set()

    def __call__(self, tree):
        for node in tree.xpath(SOURCE_XPATH):
            instance = node.attrib.get('data-silva-instance')
            parameters = parse_qs(node.attrib.get('data-silva-settings', ''))
            source = self.sources(
                TestRequest(form=parameters),
                instance=instance,
                name=node.attrib.get('data-silva-name'))
            if instance is None:
                source.create()
                instance = source.getId()
            else:
                source.save()
            node.attrib['data-source-instance'] = instance
            self.seen.add(instance)
            clean_editor_attributes(node)

    def finalize(self):
        # Remove all sources that we didn't see.
        for identifier in set(self.sources.all()).difference(self.seen):
            try:
                source = self.sources(self.request, instance=identifier)
                source.remove()
            except SourceError:
                pass

class ExternalSourceInputFilter(TransformationFilter):
    """Updater External Source information on edit.
    """
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(20)
    grok.adapts(ISourceEditableVersion, IBrowserRequest)

    def __call__(self, tree):
        for node in tree.xpath(SOURCE_XPATH):
            instance = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']
            node.attrib['data-silva-instance'] = instance


class ExternalSourceDisplayFilter(TransformationFilter):
    """Updater External Source information on edit.
    """
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(20)
    grok.adapts(ISourceEditableVersion, IBrowserRequest)

    def prepare(self, name, text):
        self.sources = getComponent(
            self.context, IExternalSourceManager)(self.context)

    def __call__(self, tree):
        for node in tree.xpath(SOURCE_XPATH):
            instance = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']
            try:
                source = self.sources(self.request, instance=instance)
                html = '<div>' + source.render() + '</div>'
            except SourceError, error:
                html = broken_source(error.to_html())

            node.insert(0, lxml.html.fromstring(html))
