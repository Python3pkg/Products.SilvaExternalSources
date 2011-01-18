# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from silva.core.interfaces import ISilvaObject, IVersionedContent
from zope.traversing.browser import absoluteURL
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

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
                            'title': source.title,
                            'url': absoluteURL(source, self.request)})
        return self.json_response(
            {'sources': sources,
             'document': getUtility(IIntIds).register(self.context)})


class PreviewSource(rest.REST):
    grok.context(ISilvaObject)
    grok.name('Products.SilvaExternalSources.source.preview')

    def POST(self, identifier):
        source = getattr(self.context, identifier, None)
        if source is not None:
            if source.is_previewable():

                parameters = {}
                for key in self.request.form:
                    if key.startswith('field_'):
                        # Only take Formulator fields.
                        parameters[key[6:]] = self.request.form[key]

                context = self.context
                if IVersionedContent.providedBy(context):
                    version = context.get_editable()
                    if version is None:
                        version = context.get_viewable()
                    if version is not None:
                        context = version

                return source.to_html(
                    version, self.request, **parameters)
            return "<b>This Code source is not previewable.</b>"
        return "<b>This Code Source doesn't exist.</b>"


class SourceParameters(rest.REST):
    """Return a form to enter and validate source paramters.
    """
    grok.context(IExternalSource)
    grok.name('Products.SilvaExternalSources.source.parameters')

    template = grok.PageTemplate(filename="templates/parameters.pt")

    def default_namespace(self):
        return {'rest': self,
                'context': self.context,
                'request': self.request}

    def namespace(self):
        return {}

    def GET(self, document):
        self.fields = []
        form = self.context.get_parameters_form()
        if form is not None:
            service = getUtility(IIntIds)
            self.request.form['model'] = service.getObject(int(document))
            # Collect field.
            for field in form.get_fields():
                label_class = ['cke_dialog_ui_labeled_label']
                if field.values.get('required'):
                    label_class.append('cke_required')
                self.fields.append(
                    { 'id': field.generate_field_html_id(),
                      'label_class': ' '.join(label_class),
                      'title': field.values.get('title'),
                      'description': field.values.get('description'),
                      'widget': field.render(None)})
        return self.template.render(self)


class SourceParametersValidator(rest.REST):
    """Validate source parameters.
    """
    grok.context(IExternalSource)
    grok.name('Products.SilvaExternalSources.source.validate')

    def POST(self, identifier, document):
        form = self.context.get_parameters_form()
        if form is not None:
            service = getUtility(IIntIds)
            self.request.form['model'] = service.getObject(int(document))
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

