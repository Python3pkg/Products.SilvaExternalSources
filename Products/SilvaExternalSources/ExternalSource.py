# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from xml.sax.saxutils import escape, unescape

from zope.interface import implements
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

# Zope
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
import Acquisition

# Silva
from Products.Silva import SilvaPermissions as permissions
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.interfaces import IEditableExternalSource
from Products.Formulator.Errors import ValidationError, FormValidationError

from silva.core.interfaces import IRoot, IVersion
from silva.translations import translate as _


module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.ExternalSource')


module_security.declarePublic('availableSources')
def availableSources(context):
    """List available sources in the site starting at context.
    """
    sources = {}
    while context is not None:
        for item in context.objectValues():
            if IExternalSource.providedBy(item) and item.id not in sources:
                sources[item.id] = item
        if IRoot.providedBy(context):
            break
        context = Acquisition.aq_parent(context)
    return sequence.sort(sources.items(), (('title', 'nocase', 'asc'),))


module_security.declarePublic('getSourceForId')
def getSourceForId(context, identifier):
    """ Look for an Source with given id. Mimic normal aqcuisition,
    but skip objects which have given id but do not implement the
    ExternalSource interface.
    """
    nearest = getattr(context, identifier, None)
    if IExternalSource.providedBy(nearest):
        return nearest
    return None


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



class ExternalSource(Acquisition.Implicit):
    implements(IExternalSource)
    security = ClassSecurityInfo()

    # XXX was management_page_charset = Converters.default_encoding
    # that doesn't work, because the add screens DON'T USE THE ZOPE
    # DEFAULT ENCODING! AAAAAAARGH

    management_page_charset = 'UTF-8'

    # Cannot make it 'private'; the form won't work in the ZMI if it was.
    parameters = None

    _data_encoding = 'UTF-8'
    _description = ''
    _is_cacheable = False
    _is_previewable = True

    # ACCESSORS

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_parameters_form')
    def get_parameters_form(self):
        """ get to the parameters form
        """
        return self.parameters


    security.declareProtected(
        permissions.AccessContentsInformation, 'get_rendered_form_for_editor')
    def get_rendered_form_for_editor(self, REQUEST=None):
        """return the rendered form"""
        assert REQUEST is not None
        get_model(REQUEST)

        xml = ['<?xml version="1.0" encoding="UTF-8" ?>\n',
                '<form id="extsourceform" action="" method="POST">\r',
                ('<input type="hidden" name="metatype" value="%s" />\n' %
                        self.meta_type),
                ('<div class="sesform">\n')]

        form = REQUEST.form.copy()
        formcopy = {}
        # pfff... what's that, not allowed to change a dict during iteration?!? ;)
        for k, v in form.iteritems():
            vtype = 'string'
            if '__type__' in k:
                k, vtype = k.split('__type__')
            formcopy[k.lower()] = v # Do a lower because the comment:
                                    # 'it seems field is always in
                                    # lower' is not quite true in fact

        form = self.get_parameters_form()
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
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8')
        return ''.join([l.encode('UTF-8') for l in xml])

    security.declareProtected(
        permissions.AccessContentsInformation, 'validate_form_to_request')
    def validate_form_to_request(self, REQUEST):
        """validate the form

            when validation succeeds return a 200 with the keys and values
            to set on the external source element in the document as an
            XML mapping, if validation fails return a 400 with the error
            message
        """
        assert REQUEST is not None
        get_model(REQUEST)

        form = self.get_parameters_form()
        values = {}
        if form is not None:
            try:
                values = form.validate_all(REQUEST)
            except FormValidationError, e:
                REQUEST.RESPONSE.setStatus(400)
                return '&'.join(['%s=%s' % (e.field['title'], e.error_text)
                                 for e in e.errors])

        REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8');

        xml = [u'<sourcedata>', u'<sourceinfo>']
        xml.append(u'<metatype>%s</metatype>' % self.meta_type)
        xml.append(u'<source_id>%s</source_id>' % self.id)
        xml.append(u'<source_title>%s</source_title>' % escape(
                ustr(self.get_title())))
        xml.append(u'<source_desc>%s</source_desc>' % escape(
                ustr(self.get_description())))
        xml.append(u'</sourceinfo>')
        xml.append(u'<params>')
        for key, value in values.items():
            value_type = type(value).__name__
            xml.append(u'<parameter type="%s" id="%s">%s</parameter>' % (
                    value_type, escape(ustr(key)), escape(ustr(value))))
        xml.append(u'</params>')
        xml.append(u'</sourcedata>')

        return u''.join(xml)

    security.declareProtected(
        permissions.AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """
        raise NotImplementedError

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_cacheable')
    def is_cacheable(self, **parameters):
        """ Specify the cacheability.
        """
        return self._is_cacheable

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_previewable')
    def is_previewable(self, **parameters):
        """ Specify the previewability (in kupu) of the source
        """
        if not hasattr(self, '_is_previewable'):
            self._is_previewable = True
        return self._is_previewable

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_data_encoding')
    def get_data_encoding(self):
        """ Specify the encoding of source's data.
        """
        return self._data_encoding

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_description')
    def get_description(self):
        """ Specify the use of this source.
        """
        return self._description

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_title')
    def get_title (self):
        return self.title


InitializeClass(ExternalSource)


class EditableExternalSource(ExternalSource):
    implements(IEditableExternalSource)
    security = ClassSecurityInfo()

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_form')
    def set_form(self, form):
        """ Set Formulator parameters form
        """
        self.parameters = form

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        """ set encoding of data
        """
        self._data_encoding = encoding

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_description')
    def set_description(self, description):
        """ set description of external source's use
        """
        self._description = description

    security.declareProtected(
        permissions.ViewManagementScreens, 'set_cacheable')
    def set_cacheable(self, cacheable):
        """ set cacheablility of source
        """
        self._is_cacheable = cacheable

    security.declareProtected(permissions.ViewManagementScreens, 'set_previewable')
    def set_previewable(self, previewable):
        """ set previewablility (in kupu) of source
        """
        self._is_previewable = not not previewable


InitializeClass(EditableExternalSource)
