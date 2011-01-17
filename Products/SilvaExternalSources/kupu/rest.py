# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from xml.sax.saxutils import escape, unescape

from five import grok
from infrae import rest
from silva.core.interfaces import IVersion, ISilvaObject
from silva.translations import translate as _
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError
from Products.SilvaExternalSources.ExternalSource import getSourceForId
from Products.SilvaExternalSources.interfaces import IExternalSource, ICodeSource


def urepr(l):
    l = repr(l)
    if l[0] == 'u':
        l = l[1:]
    return l


def ustr(text, enc='utf-8'):
    if text is None:
        return u''
    elif type(text) == type(''):
        return unicode(text, enc, 'replace')
    elif type(text) == type(u''):
        return text
    elif type(text) == type([]):
        return u"[%s]" % u', '.join([urepr(l) for l in text])
    elif type(text) == type(True):
        return text and '1' or '0'
    else:
        return unicode(str(text), enc, 'replace')


def get_model(request):
    if 'docref' in request.form and request.form['docref']:
        # XXX don't like to do this, this should go away (sylvain)
        model = getUtility(IIntIds).getObject(int(request['docref']))
        if IVersion.providedBy(model):
            request.form['version'] = model
            model = model.get_content()
        request.form['model'] = model



class SourceUrl(rest.REST):
    grok.context(ISilvaObject)
    grok.name('Products.SilvaExternalSources.kupu.url')
    grok.require('zope2.AccessContentsInformation')

    def GET(self, id):
        source = getSourceForId(self.context, id)
        if source is not None:
            return source.absolute_url()
        return ''


class ParameterForm(rest.REST):
    grok.context(IExternalSource)
    grok.name('Products.SilvaExternalSources.kupu.form')
    grok.require('zope2.AccessContentsInformation')

    def render_form(self):
        get_model(self.request)

        xml = ['<form id="extsourceform" action="" method="POST">\n',
                ('<input type="hidden" name="metatype" value="%s" />\n' %
                        self.context.meta_type),
                ('<div class="sesform">\n')]

        form = self.request.form.copy()
        formcopy = {}
        # pfff... what's that, not allowed to change a dict during iteration?!? ;)
        for k, v in form.iteritems():
            vtype = 'string'
            if '__type__' in k:
                k, vtype = k.split('__type__')
            formcopy[k.lower()] = v # Do a lower because the comment:
                                    # 'it seems field is always in
                                    # lower' is not quite true in fact

        form = self.context.get_parameters_form()
        if form is not None:
            for field in form.get_fields():
                value = None
                #the field id is actually _always_ lowercase in formcopy
                # (see https://bugs.launchpad.net/silva/+bug/180860)
                field_id = field.id.lower()

                fieldDescription = ustr(field.values.get('description',''), 'UTF-8')
                if fieldDescription:
                    fieldCssClasses = "rollover"
                    fieldDescription = '<span class="tooltip">%s</span>'%fieldDescription
                else:
                    fieldCssClasses = ""
                if field.values.get('required',False):
                    fieldCssClasses += ' requiredfield'
                if fieldCssClasses:
                    fieldCssClasses = 'class="%s"'%fieldCssClasses.strip()

                xml.append('<div class="fieldblock">\n<label for="field-%s"><a href="#" onclick="return false" %s>%s%s</a></label>\n' % (
                    field_id.replace('_', '-'), fieldCssClasses, fieldDescription, ustr(field.values['title'], 'UTF-8'))
                    )

                if formcopy.has_key(field_id):
                    value = formcopy[field_id]
                if value is None:
                    # default value (if available)
                    value = field.get_value('default')
                if type(value) == list:
                    value = [ustr(unescape(x), 'UTF-8') for x in value]
                elif field.meta_type == "CheckBoxField":
                    value = int(value)
                elif field.meta_type == "DateTimeField":
                    if value:
                        value = DateTime(value)
                    else: # it needs to be None, rather than ''
                        value = None
                else:
                    if value is None:
                        value = ''
                    value = ustr(unescape(value), 'UTF-8')
                xml.append('%s\n</div>\n' %
                                (field.render(value)))

        # if a Code Source has no parameters, inform the user how to proceed
        if form is None or len(form.get_fields()) == 0:
            no_params = _('This Code Source has no adjustable settings. Click a button to insert or remove it.')
            xml.append('<p class="messageblock">%s</p>' % no_params)

        xml.append('</div>\n</form>\n')
        self.request.RESPONSE.setHeader('Content-Type', 'text/html;charset=UTF-8')
        return ''.join([l.encode('UTF-8') for l in xml])

    def GET(self):
        return self.render_form()

    def POST(self):
        return self.render_form()


class CodeSourceParameterForm(ParameterForm):
    grok.context(ICodeSource)

    def render_form(self):
        html = super(CodeSourceParameterForm, self).render_form()
        if self.context.is_elaborate():
            root_url = self.context.get_root_url()
            html = html.replace(
                '<form ', '<html><head>'
                '<style media="all" type="text/css" xml:space="preserve">'
                '@import url(%s);</style>'
                '<link href="%s" rel="stylesheet" type="text/css" />'
                '<link href="%s" type="text/css" rel="stylesheet" />'
                '</head><body><div class="kupu-toolbox-active"><div'
                ' class="kupu-tooltray"><div '
                'id="kupu-extsource-formcontainer"><form class="elaborate" '
                % (root_url + '/++resource++silva.core.smi/smi.css',
                   root_url + '/globals/silvaContentStyle.css',
                   'kupustyles.css',))
            html = html.replace(
                '</form>', '<input name="update_button" type="button"'
                ' class="button" value="update"'
                ' onClick="window.opener.kupu.tools.extsourcetool._form='
                'window.document.forms[0];window.opener.kupu.tools.'
                'extsourcetool._validateAndSubmit(true);window.close()">'
                '</form></div></div><div></body></html>')
        return html


class ValidateForm(rest.REST):
    grok.context(IExternalSource)
    grok.name('Products.SilvaExternalSources.kupu.validate')
    grok.require('zope2.AccessContentsInformation')

    def POST(self):
        get_model(self.request)

        form = self.context.get_parameters_form()
        values = {}
        if form is not None:
            try:
                values = form.validate_all(self.request)
            except FormValidationError, e:
                self.request.RESPONSE.setStatus(400)
                return '&'.join(['%s=%s' % (e.field['title'], e.error_text)
                                 for e in e.errors])

        self.request.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8');

        xml = [u'<sourcedata>', u'<sourceinfo>']
        xml.append(u'<metatype>%s</metatype>' % self.context.meta_type)
        xml.append(u'<source_id>%s</source_id>' % self.context.id)
        xml.append(u'<source_title>%s</source_title>' % escape(
                ustr(self.context.get_title())))
        xml.append(u'<source_desc>%s</source_desc>' % escape(
                ustr(self.context.get_description())))
        xml.append(u'</sourceinfo>')
        xml.append(u'<params>')
        for key, value in values.items():
            value_type = type(value).__name__
            xml.append(u'<parameter type="%s" id="%s">%s</parameter>' % (
                    value_type, escape(ustr(key)), escape(ustr(value))))
        xml.append(u'</params>')
        xml.append(u'</sourcedata>')

        return u''.join(xml)


class PreviewSource(rest.REST):
    grok.context(ISilvaObject)
    grok.name('Products.SilvaExternalSources.kupu.preview')
    grok.require('zope2.AccessContentsInformation')

    def POST(self):
        parameters = self.request.form.copy()
        source_id = parameters.get("source_id", "")
        docref = parameters.get("docref", "")
        if source_id  and docref:
            source = getattr(self.context, source_id, None)
            if source is None:
                return u""
            if source.is_previewable():
                del parameters['source_id']
                del parameters['docref']
                version = getUtility(IIntIds).getObject(int(docref))
                return source.to_html(
                    version, self.request, **parameters)
        return u""
