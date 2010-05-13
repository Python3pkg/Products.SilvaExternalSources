# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from sprout.saxext.html2sax import saxify
from zope.interface import Interface

from Products.Silva.silvaxml.xmlexport import (
    VersionedContentProducer, SilvaBaseProducer)
from Products.ParsedXML.DOM.Core import Node
from Products.SilvaDocument.silvaxml.xmlexport import NS_SILVA_DOCUMENT
from Products.SilvaExternalSources.ExternalSource import getSourceForId
from Products.SilvaExternalSources.interfaces import IExternalSource


class ExternalSourceProducer(SilvaBaseProducer):
    grok.adapts(IExternalSource, Interface)

    def sax(self):
        source = getSourceForId(self.context, self.context.id)
        parameters = {}
        for child in node.childNodes:
            if child.nodeName == 'parameter':
                self.startElementNS(SilvaDocumentNS, 'parameter', {'key': child.attributes['key'].value})
                for grandChild in child.childNodes:
                    text = ''
                    if grandChild.nodeType == Node.TEXT_NODE:
                        if grandChild.nodeValue:
                            self.handler.characters(grandChild.nodeValue)
                            text = text + grandChild.nodeValue
                parameters[str(child.attributes['key'].value)] = text
                self.endElementNS(SilvaDocumentNS, 'parameter')
        if self.getSettings().externalRendering():
            html = source.to_html(self.context.REQUEST, **parameters)
            self.render_html(html)

