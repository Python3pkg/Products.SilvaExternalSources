# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.base import TransformationFilter
from silva.core.interfaces import IVersion
from zope.publisher.interfaces.browser import IBrowserRequest


class ExternalSourceTransformationFilter(TransformationFilter):
    """Process External Source information on save.
    """
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)
    grok.order(20)
    grok.adapts(IVersion, IBrowserRequest)

    def __call__(self, tree):
        for source in tree.xpath('//div[@class="external-source"]'):
            pass
