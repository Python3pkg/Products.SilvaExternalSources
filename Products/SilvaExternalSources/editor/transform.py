# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
import lxml.html

from five import grok
from silva.core.editor.transform.interfaces import (
    ISaveEditorFilter, IInputEditorFilter, IDisplayFilter)
from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.editor.output import clean_editor_attributes
from silva.core.interfaces import IVersion
from zope.publisher.interfaces.browser import IBrowserRequest

from Products.SilvaExternalSources.editor.interfaces import ISourceInstances


SOURCE_XPATH = '//div[contains(@class, "external-source")]'


class ExternalSourceSaveFilter(TransformationFilter):
    """Process External Source information on save.
    """
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)
    grok.order(20)
    grok.adapts(IVersion, IBrowserRequest)

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)
        self.seen_sources = set()

    def __call__(self, tree):
        for source in tree.xpath(SOURCE_XPATH):
            if 'data-silva-instance' in source.attrib:
                identifier = source.attrib['data-silva-instance']
            else:
                identifier = self.sources.new(
                    source.attrib['data-silva-name'])
            parameters = source.attrib.get('data-silva-settings')
            if parameters is not None:
                instance = self.sources.bind(
                    identifier, self.context, self.request)
                instance.update(parameters)
            source.attrib['data-source-instance'] = identifier
            self.seen_sources.add(identifier)
            clean_editor_attributes(source)

    def finalize(self):
        # Remove all sources that we didn't see.
        all_sources = set(self.sources.keys())
        for identifier in all_sources.difference(self.seen_sources):
            self.sources.remove(identifier, self.context, self.request)


class ExternalSourceInputFilter(TransformationFilter):
    """Updater External Source information on edit.
    """
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(20)
    grok.adapts(IVersion, IBrowserRequest)

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)

    def __call__(self, tree):
        for source in tree.xpath(SOURCE_XPATH):
            identifier = source.attrib['data-source-instance']
            del source.attrib['data-source-instance']
            source.attrib['data-silva-instance'] = identifier
            instance = self.sources.bind(
                identifier, self.context, self.request)
            source.attrib['data-silva-name'] = instance.identifier


class ExternalSourceDisplayFilter(TransformationFilter):
    """Updater External Source information on edit.
    """
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(20)
    grok.adapts(IVersion, IBrowserRequest)

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)

    def __call__(self, tree):
        for source in tree.xpath(SOURCE_XPATH):
            identifier = source.attrib['data-source-instance']
            del source.attrib['data-source-instance']
            instance = self.sources.bind(
                identifier, self.context, self.request)
            html = lxml.html.fromstring('<div>' + instance.render() + '</div>')
            source.insert(0, html)
