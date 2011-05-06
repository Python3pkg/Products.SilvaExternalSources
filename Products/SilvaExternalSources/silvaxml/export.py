from five import grok

from silva.core.interfaces import IVersion, IExportSettings
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
    grok.adapts(IVersion, IExportSettings)
    grok.provides(ISilvaXMLExportFilter)

    def __init__(self, context, settings):
        self.context = context
        self.settings = settings

    def prepare(self, name, text):
        self.sources = ISourceInstances(text)

    def __call__(self, tree):
        for node in tree.xpath(transform.SOURCE_XPATH):
            identifier = node.attrib['data-source-instance']
            del node.attrib['data-source-instance']
            instance = self.sources.bind(
                identifier, self.context, self.settings.request)
            source, form = instance.get_source_and_form()
            root = self.settings.getExportRoot()
            path = relative_path(
                root.getPhysicalPath(), source.getPhysicalPath())
            node.attrib['source-path'] = canonical_path(
                "/".join(path))

            producer = FieldProducer(root=node)
            producer.startDocument()
            producer.startPrefixMapping(None, NS_URI)
            producer.startElement('fields')
            for field in form.fields(ignore_content=False):
                producer.startElement('field', {(None, 'id'): field.id})
                field._field.validator.serializeValue(
                    field._field, field._value, producer)
                producer.endElement('field')
            producer.endElement('fields')
            producer.endDocument()


