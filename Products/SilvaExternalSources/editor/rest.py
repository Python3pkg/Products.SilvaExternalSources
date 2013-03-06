# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from grokcore.chameleon.components import ChameleonPageTemplate
from zeam.component import getComponent

from silva.ui.rest import UIREST
from silva.core.interfaces import ISilvaObject, IVersionedContent
from silva.core.views import views as silvaviews

from ..interfaces import availableSources
from ..interfaces import IExternalSourceManager
from ..errors import SourceError

from Products.Formulator.zeamsupport import IFormulatorField

# Define the CSS class names to use with CKE editor.
STYLES = {'ListField': {'css_class': 'cke_dialog_ui_input_select'},
          'MultiListField': {'css_class': 'cke_dialog_ui_input_select'},
          'StringField': {'css_class': 'cke_dialog_ui_input_text'},
          'IntegerField': {'css_class': 'cke_dialog_ui_input_text'},
          'EmailField': {'css_class': 'cke_dialog_ui_input_text'},
          'PatternField': {'css_class': 'cke_dialog_ui_input_text'},
          'TextAreaField': {'css_class': 'cke_dialog_ui_input_textarea'},
          'RawTextAreaField': {'css_class': 'cke_dialog_ui_input_textarea'},
          'ListTextAreaField': {'css_class': 'cke_dialog_ui_input_textarea'},
          'LinesField': {'css_class': 'cke_dialog_ui_input_textarea'},
          'EmailLinesField': {'css_class': 'cke_dialog_ui_input_textarea'},
          'PasswordField': {'css_class': 'cke_dialog_ui_input_password'}}


class ListAvailableSources(UIREST):
    """List all available sources.
    """
    grok.context(ISilvaObject)
    grok.name('Products.SilvaExternalSources.source.availables')

    def GET(self):
        sources = []
        for identifier, source in availableSources(self.context):
            sources.append({'identifier': identifier,
                            'title': source.get_title()})
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
        source = getComponent(document, IExternalSourceManager)(document)(
            self.request,
            instance=self.request.get('source_instance'),
            name=self.request.get('source_name'))
        source.ignoreContent = 'source_name' in self.request.form
        source.ignoreRequest = 'source_inline' not in self.request.form
        return source


class PreviewSource(SourceAPI):
    grok.name('Products.SilvaExternalSources.source.preview')

    def POST(self):
        try:
            return self.get_source().render(preview=True)
        except SourceError as error:
            return silvaviews.render(error, self.request, preview=True)


class SourceParameters(SourceAPI):
    """Return a form to enter and validate source paramters.
    """
    grok.name('Products.SilvaExternalSources.source.parameters')

    template = ChameleonPageTemplate(filename="templates/parameters.cpt")

    def default_namespace(self):
        return {'rest': self,
                'context': self.context,
                'request': self.request}

    def namespace(self):
        return {}

    def POST(self):
        self.fields = []
        try:
            source = self.get_source()
        except SourceError:
            pass
        else:
            # Apply formulator styles. No choice here.
            for field in source.fields:
                if IFormulatorField.providedBy(field):
                    if field.meta_type in STYLES:
                        field.customize(STYLES[field.meta_type])

            for widget in source.fieldWidgets(
                ignoreRequest=False, ignoreContent=False):
                label_class = ['cke_dialog_ui_labeled_label']
                if widget.required:
                    label_class.append('cke_required')
                self.fields.append(
                    {'identifier': widget.htmlId(),
                     'label_class': ' '.join(label_class),
                     'title': widget.title,
                     'description': widget.description,
                     'widget': widget.render()})
        return self.template.render(self)


class SourceParametersValidator(SourceAPI):
    """Validate source parameters.
    """
    grok.name('Products.SilvaExternalSources.source.validate')

    def POST(self):
        source = self.get_source()
        if source is not None:
            values, errors = source.extractData(source.fields)
            if errors:
                return self.json_response(
                    {'success': False,
                     'messages': [
                            {'identifier': error.identifier,
                             'message': error.title}
                            for error in errors]})
        return self.json_response({'success': True})

