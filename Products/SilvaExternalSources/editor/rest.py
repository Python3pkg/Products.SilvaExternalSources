# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.ui.rest import UIREST
from silva.core.interfaces import ISilvaObject, IVersionedContent
from silva.core.editor.interfaces import IText
from zope.component import getMultiAdapter

from Products.SilvaExternalSources.ExternalSource import availableSources
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances
from Products.Formulator.interfaces import IBoundForm


class ListAvailableSources(UIREST):
    """List all available sources.
    """
    grok.context(ISilvaObject)
    grok.name('Products.SilvaExternalSources.source.availables')

    def GET(self):
        sources = []
        for identifier, source in availableSources(self.context):
            sources.append({'identifier': identifier,
                            'title': source.title})
        return self.json_response(sources)


class SourceAPI(UIREST):
    grok.context(ISilvaObject)
    grok.baseclass()

    def get_document(self):
        if IVersionedContent.providedBy(self.context):
            version = self.context.get_editable()
            if version is not None:
                return version
            version = self.context.get_viewable()
            if version is not None:
                return version
        return self.context

    def get_source(self):
        """Return the External Source and form associated with the
        given request.
        """
        document = self.get_document()

        # This is an existing source instance
        instance = self.request.get('source_instance')
        text_attribute = self.request.get('source_text')
        if instance is not None and text_attribute is not None:
            text = getattr(document, text_attribute, None)
            if text is not None and IText.providedBy(text):
                sources = ISourceInstances(text)
                instance = sources.bind(instance, document, self.request)
                return instance.get_source_and_form()

        # No existing instance, fetch a new source.
        identifier = self.request.get('source_name')
        if identifier is not None:
            source = getattr(self.context, identifier, None)
            if source is not None:
                if IExternalSource.providedBy(source):
                    form = None
                    formulator_form = source.get_parameters_form()
                    if formulator_form is not None:
                        # If there is a formulator form, query its binding.
                        form = getMultiAdapter(
                            (formulator_form, self.request, document),
                            IBoundForm)
                    return source, form

        return None, None

    def get_parameters(self, form):
        """Extract External Source parameters (formulator) from the
        request.
        """
        if form is not None:
            if 'source_inline' in self.request.form:
                return form.extract()
            return form.read()
        # There is no form, so no parameters
        return {}


class PreviewSource(SourceAPI):
    grok.name('Products.SilvaExternalSources.source.preview')

    def POST(self):
        source, form = self.get_source()
        if source is not None:
            if source.is_previewable():
                parameters = self.get_parameters(form)
                document = self.get_document()

                return source.to_html(
                    document, self.request, **parameters)
            return "<b>This Code source is not previewable.</b>"
        return "<b>Impossible to find this source.</b>"


class SourceParameters(SourceAPI):
    """Return a form to enter and validate source paramters.
    """
    grok.name('Products.SilvaExternalSources.source.parameters')

    template = grok.PageTemplate(filename="templates/parameters.pt")

    def default_namespace(self):
        return {'rest': self,
                'context': self.context,
                'request': self.request}

    def namespace(self):
        return {}

    def POST(self):
        source, form = self.get_source()
        self.fields = []
        if form is not None:
            # Collect field.
            is_inline = 'source_inline' not in self.request.form
            for field in form.fields(
                ignore_request=is_inline, ignore_content=not is_inline):
                label_class = ['cke_dialog_ui_labeled_label']
                if field.required:
                    label_class.append('cke_required')
                self.fields.append(
                    { 'id': field.id,
                      'label_class': ' '.join(label_class),
                      'title': field.title,
                      'description': field.description,
                      'widget': field()})
        return self.template.render(self)


class SourceParametersValidator(SourceAPI):
    """Validate source parameters.
    """
    grok.name('Products.SilvaExternalSources.source.validate')

    def POST(self):
        source, form = self.get_source()
        if form is not None:
            # For hacked parameters
            self.request.form['model'] = self.context
            try:
                form.validate()
            except ValueError as error:
                return self.json_response(
                    {'success': False,
                     'messages': [
                            {'identifier': e.field.generate_field_html_id(),
                             'message': e.error_text}
                            for e in error.args[0]]})
        return self.json_response({'success': True})

