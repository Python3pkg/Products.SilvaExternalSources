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
from Products.Silva import SilvaPermissions
from Products.SilvaExternalSources.interfaces import IExternalSource
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

    meta_type = "Silva External Source"

    security = ClassSecurityInfo()

    # XXX was management_page_charset = Converters.default_encoding
    # that doesn't work, because the add screens DON'T USE THE ZOPE
    # DEFAULT ENCODING! AAAAAAARGH

    management_page_charset = 'UTF-8'

    # Cannot make it 'private'; the form won't work in the ZMI if it was.
    parameters = None

    _data_encoding = 'UTF-8'
    _description = ''
    _is_cacheable = 0
    # if true, the rendered source is displayed in kupu, given
    # the parameters specified in the doc.
    _is_previewable = True

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,'form')
    def form(self):
        """ get to the parameters form
        """
        return self.parameters


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_rendered_form_for_editor')
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

        form = self.form()
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'validate_form_to_request')
    def validate_form_to_request(self, REQUEST):
        """validate the form

            when validation succeeds return a 200 with the keys and values
            to set on the external source element in the document as an
            XML mapping, if validation fails return a 400 with the error
            message
        """
        assert REQUEST is not None
        get_model(REQUEST)

        form = self.form()
        if form is None:
            REQUEST.RESPONSE.setStatus(400)
            return 'No parameters need to be validated'
        try:
            result = form.validate_all(REQUEST)
        except FormValidationError, e:
            REQUEST.RESPONSE.setStatus(400)
            return '&'.join(['%s=%s' % (e.field['title'], e.error_text)
                                for e in e.errors])

        REQUEST.RESPONSE.setHeader('Content-Type',
                                   'text/xml;charset=UTF-8');
        xml = self._formresult_to_xml(result)
        return xml

    def _formresult_to_xml(self, formresult):
        """returns a result dictionary as an xml mapping"""
        xml = ['<sourcedata>','<sourceinfo>']
        xml.append('<metatype>%s</metatype>' % self.meta_type)
        xml.append('<source_id>%s</source_id>' % self.id)
        xml.append('<source_title>%s</source_title>' % escape(
                ustr(self.get_title())))
        xml.append('<source_desc>%s</source_desc>' % escape(
                ustr(self.description())))
        xml.append('</sourceinfo>')
        xml.append('<params>')
        for key, value in formresult.items():
            value_type = type(value).__name__
            xml.append('<parameter type="%s" id="%s">%s</parameter>' % (
                    value_type, escape(ustr(key)), escape(ustr(value))))
        xml.append('</params>')
        xml.append('</sourcedata>')
        return ''.join(xml)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """
        raise NotImplementedError

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'is_cacheable')
    def is_cacheable(self, **kw):
        """ Specify the cacheability.
        """
        return self._is_cacheable

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                 'is_previewable')
    def is_previewable(self, **kw):
        """ Specify the previewability (in kupu) of the source
        """
        if not hasattr(self, '_is_previewable'):
            self._is_previewable = True
        return self._is_previewable

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'data_encoding')
    def data_encoding(self):
        """ Specify the encoding of source's data.
        """
        return self._data_encoding

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'description')
    def description(self):
        """ Specify the use of this source.
        """
        return self._description

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_title')
    def get_title (self):
        return self.title

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ render HTML with default or other test values in ZMI for
        purposes of testing the ExternalSource.
        """
        form = self.form()
        if REQUEST is not None and form:
            if not hasattr(REQUEST, 'model'):
                REQUEST.model = self
            try:
                kw = form.validate_all(REQUEST)
            except (FormValidationError, ValidationError):
                # If we cannot validate (e.g. due to required parameters),
                # return a form.
                # FIXME: How to get some feedback in the rendered page? E.g.
                # in case of validation errors.
                return form.render(REQUEST=REQUEST)
        else:
            kw = {}

        return self.to_html(REQUEST, **kw)

    # MODIFIERS

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'set_form')
    def set_form(self, form):
        """ Set Formulator parameters form
        """
        self.parameters = form

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        """ set encoding of data
        """
        self._data_encoding = encoding

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'set_description')
    def set_description(self, desc):
        """ set description of external source's use
        """
        self._description = desc

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'set_is_cacheable')
    def set_is_cacheable(self, cacheable):
        """ set cacheablility of source
        """
        self._is_cacheable = cacheable

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'set_is_previewable')
    def set_is_previewable(self, previewable):
        """ set previewablility (in kupu) of source
        """
        self._is_previewable = not not previewable


InitializeClass(ExternalSource)
