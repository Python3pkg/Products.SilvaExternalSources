# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml.html
import logging

from five import grok
from zeam.component import getComponent
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest

from silva.core.views import views as silvaviews
from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.editor.output import clean_editor_attributes
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from zeam.form import silva as silvaforms

from ..interfaces import IExternalSourceManager
from ..interfaces import ISourceEditableVersion
from ..errors import SourceError
from ..editor.utils import parse_qs

logger = logging.getLogger('silva.externalsources')
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
        self.manager = getComponent(
            self.context, IExternalSourceManager)(self.context)
        self.seen = set()

    def __call__(self, tree):
        for node in tree.xpath(SOURCE_XPATH):
            name = node.attrib.get('data-silva-name')
            instance = node.attrib.get('data-silva-instance')
            changed = 'data-silva-settings' in node.attrib
            parameters = parse_qs(node.attrib.get('data-silva-settings', ''))
            try:
                source = self.manager(
                    TestRequest(form=parameters), instance=instance, name=name)
            except SourceError:
                logger.error(
                    u'Broken source %s(%s) on content %s',
                    name, instance, '/'.join(self.context.getPhysicalPath()))
            else:
                if instance is None:
                    status = source.create()
                    instance = source.getId()
                elif changed:
                    status = source.save()
                if changed and status is silvaforms.FAILURE:
                    logger.error(
                        u"Error while saving source parameters %s "
                        u"for %s(%s) on content %s",
                        parameters, name, instance,
                        '/'.join(self.context.getPhysicalPath()))
                node.attrib['data-source-instance'] = instance
                self.seen.add(instance)
            clean_editor_attributes(node)

    def finalize(self):
        # Remove all sources that we didn't see.
        for identifier in set(self.manager.all()).difference(self.seen):
            try:
                source = self.manager(self.request, instance=identifier)
                source.remove()
            except SourceError:
                logger.error(
                    'Error while removing source %s from text %s',
                    identifier, '/'.join(self.context.getPhysicalPath()))

    def truncate(self, name, text):
        manager = getComponent(
            self.context, IExternalSourceManager)(self.context)
        for identifier in manager.all():
            try:
                source = manager(self.request, instance=identifier)
                source.remove()
            except SourceError:
                logger.error(
                    'Error while removing source %s from text %s',
                    identifier, '/'.join(self.context.getPhysicalPath()))


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
                html = silvaviews.render(error, self.request).strip()
                if not html:
                    continue
                html = broken_source(html)

            node.insert(0, lxml.html.fromstring(html))
