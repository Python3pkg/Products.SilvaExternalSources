# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from silva.core.interfaces import ISilvaObject
from zope.traversing.browser import absoluteURL

from Products.SilvaExternalSources.ExternalSource import availableSources
from Products.SilvaExternalSources.interfaces import IExternalSource


class ListAvailableSources(rest.REST):
    """List all available sources.
    """
    grok.context(ISilvaObject)
    grok.name('Products.SilvaExternalSources.sources.available')

    def GET(self):
        sources = []
        for identifier, source in availableSources(self.context):
            sources.append({'identifier': identifier,
                            'title': source.title,
                            'url': absoluteURL(source, self.request)})
        return self.json_response({'sources': sources})


class SourceParameters(rest.REST):
    """Return a form to enter and validate source paramters.
    """
    grok.context(IExternalSource)
    grok.name('Products.SilvaExternalSources.sources.parameters')

    def GET(self):
        pass
