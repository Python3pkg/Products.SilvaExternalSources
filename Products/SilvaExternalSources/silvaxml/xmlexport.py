from five import grok

from silva.core.interfaces import IVersion, ISilvaXMLExportHandler
from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.interfaces import ISilvaXMLExportFilter
from Products.SilvaExternalSources.editor import transform
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances
from Products.SilvaExternalSources.silvaxml import NS_URI
from Products.SilvaExternalSources.silvaxml.treehandler import \
    ElementTreeContentHandler
from silva.core.references.reference import relative_path, canonical_path


class FieldProducer(ElementTreeContentHandler):
    @property
    def handler(self):
        return self


class ExternalSourceExportFilter(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLExportHandler)
    grok.provides(ISilvaXMLExportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)

    def __call__(self, tree):
        for node in tree.xpath(transform.SOURCE_XPATH):
            identifier = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']
            settings = self.handler.getSettings()
            instance = self.sources.bind(
                identifier, self.context, settings.request)
            source, form = instance.get_source_and_form()
            root = settings.getExportRoot()
            path = relative_path(
                root.getPhysicalPath(), source.getPhysicalPath())
            node.attrib['source-path'] = canonical_path(
                "/".join(path))

            producer = FieldProducer(root=node)
            producer.startPrefixMapping(None, NS_URI)
            producer.startElement('fields')
            for field in form.fields(ignore_content=False):
                producer.startElement('field', {(None, 'id'): field.id})
                field.serialize(producer)
                producer.endElement('field')
            producer.endElement('fields')


