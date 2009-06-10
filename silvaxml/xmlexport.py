from Products.Silva.silvaxml.xmlexport import theXMLExporter, VersionedContentProducer, SilvaBaseProducer
from sprout.saxext.html2sax import saxify
from Products.ParsedXML.DOM.Core import Node
from Products.SilvaExternalSources import ExternalSource
from Products.SilvaExternalSources.ExternalSource import getSourceForId

SilvaDocumentNS = 'http://infrae.com/namespace/silva-document'

def initializeXMLExportRegistry():
    """Here the actual content types are registered.
    """
    from Products.SilvaDocument.Document import Document, DocumentVersion
    exporter = theXMLExporter
    exporter.registerNamespace('doc', SilvaDocumentNS)
    exporter.registerProducer(ExternalSource, ExternalSourceProducer)

class ExternalSourceProducer(SilvaBaseProducer):
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

