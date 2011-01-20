# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from silva.core.interfaces import ISilvaObject, IVersionedContent

from Products.SilvaExternalSources.ExternalSource import availableSources
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.Formulator.Errors import FormValidationError


class ListAvailableSources(rest.REST):
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


class SourceAPI(rest.REST):
    grok.context(ISilvaObject)
    grok.baseclass()

    def get_source(self, identifier):
        """Return the External Source associated with the given
        identifier.
        """
        source = getattr(self.context, identifier, None)
        if source is not None:
            if IExternalSource.providedBy(source):
                return source
        return source

    def get_parameters(self):
        """Extract External Source parameters (formulator) from the
        request.
        """
        parameters = {}
        for key in self.request.form:
            if key.startswith('field_'):
                # Only take Formulator fields.
                parameters[key[6:]] = self.request.form[key]
        return parameters


class PreviewSource(SourceAPI):
    grok.name('Products.SilvaExternalSources.source.preview')

    def POST(self, identifier):
        source = self.get_source(identifier)
        if source is not None:
            if source.is_previewable():
                parameters = self.get_parameters()

                model = self.context
                if IVersionedContent.providedBy(model):
                    version = model.get_editable()
                    if version is None:
                        version = model.get_viewable()
                    if version is not None:
                        model = version

                return source.to_html(
                    model, self.request, **parameters)
            return "<b>This Code source is not previewable.</b>"
        return "<b>This Code Source doesn't exist.</b>"


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

    def POST(self, identifier):
        source = self.get_source(identifier)
        self.identifier = identifier
        self.fields = []
        form = source.get_parameters_form()
        parameters = self.get_parameters()
        if form is not None:
            self.request.form['model'] = self.context
            # Collect field.
            for field in form.get_fields():
                label_class = ['cke_dialog_ui_labeled_label']
                if field.values.get('required'):
                    label_class.append('cke_required')
                value = parameters.get(field.id)
                self.fields.append(
                    { 'id': field.generate_field_html_id(),
                      'label_class': ' '.join(label_class),
                      'title': field.values.get('title'),
                      'description': field.values.get('description'),
                      'widget': field.render(value)})
        return self.template.render(self)


class SourceParametersValidator(SourceAPI):
    """Validate source parameters.
    """
    grok.name('Products.SilvaExternalSources.source.validate')

    def POST(self, identifier):
        source = self.get_source(identifier)
        form = source.get_parameters_form()
        if form is not None:
            self.request.form['model'] = self.context
            try:
                form.validate_all(self.request)
            except FormValidationError as failure:
                return self.json_response(
                    {'success': False,
                     'messages': [
                            {'identifier': e.field.generate_field_html_id(),
                             'message': e.error_text}
                            for e in failure.errors]})
        return self.json_response({'success': True})

