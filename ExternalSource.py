# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.15 $
from interfaces import IExternalSource
# Zope
import Acquisition
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens
# Interfaces
from Products.Silva.interfaces import IRoot
# Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.Errors import ValidationError, FormValidationError

icon="www/silvaexternalsource.png"

module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.ExternalSource')

class _AvailableSources:
    """SINGLETON

    Helps getting a list of ExternalSources from context up.
    Stop at the "Silva Root".
    """

    def _list(self, context):
        """ Recurse through parents up. 
        
        Returns list of tuples of (id, object)
        
        Only lists source's that can be reached from the context 
        through acquisition.
        """
        sources = {}
        while 1:
            objs = context.objectValues()
            for obj in objs:
                if IExternalSource.isImplementedBy(obj):
                    if not sources.has_key(obj.id):
                        sources[obj.id] = obj
            if IRoot.isImplementedBy(context):
                # stop at Silva Root
                break
            context = context.aq_parent
        return sources.items()

    def __call__(self, context):         
        return self._list(context)

module_security.declarePublic('availableSources')
availableSources = _AvailableSources()

module_security.declarePublic('getSourceForId')
def getSourceForId(context, id):
    """ Look for an Source with given id. Mimic normal aqcuisition, 
    but skip objects which have given id but do not implement the 
    ExternalSource interface.
    """
    nearest = getattr(context, id, None)
    if nearest is None:
        return None
    if IExternalSource.isImplementedBy(nearest):
        return nearest    
    if IRoot.isImplementedBy(context):
        return None
    else:
        return getSourceForId(context.aq_parent, id)    

# helper function copied from 
# SilvaDocument/widgets/element/doc_element/source/mode_edit/save_helper.py
def ustr(text, enc='utf-8'):
    if text is None:
        return u''
    elif type(text) == type(''):
        return unicode(text, enc, 'replace')
    elif type(text) == type(u''):
        return text
    else:
        return unicode(str(text), enc, 'replace')

class ExternalSource(Acquisition.Implicit):

    __implements__ = IExternalSource
    
    meta_type = "Silva External Source"

    security = ClassSecurityInfo()

    management_page_charset = 'utf-8'
    
    parameters = None # Cannot make it 'private'; the form won't work in the ZMI if it was.

    _data_encoding = 'ISO-8859-15'
    _description = ''
    _is_cacheable = 0

    def __init__(self, id, title):
        self.id = id
        self.title = title

    # ACCESSORS

    def form(self):
        """ get to the parameters form
        """
        return self.parameters

    def get_rendered_form_for_editor(self, REQUEST=None):
        """return the rendered form"""
        print repr(REQUEST.form)
        xml = ['<?xml version="1.0" encoding="UTF-8" ?>\n',
                '<form action="" method="POST">',
                '<table width="100%" id="extsourceform" style="display: block" class="plain">']
        for field in self.parameters.get_fields():
            xml.append('<tr><td>%s</td>' % field.title())
            value = None
            if REQUEST.form.has_key(field.id):
                value = REQUEST.form[field.id]
            xml.append('<td>%s</td></tr>' % (field.render(value)))
        xml.append('</table></form>')
        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8')
        return ''.join(xml)

    def validate_form_to_request(self, REQUEST):
        """validate the form
        
            when validation succeeds return a 200 with the keys and values
            to set on the external source element in the document as an
            XML mapping, if validation fails return a 400 with the error
            message
        """
        form = self.parameters
        print repr(REQUEST.form)
        try:
            result = form.validate_all(REQUEST)
        except FormValidationError, e:
            REQUEST.RESPONSE.setStatus(400, 'Bad Request')
            return '&'.join(['%s=%s' % (e.field['title'], e.error_text) for e in e.errors])
        else:
            REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml');
            xml = self._formresult_to_xml(result)
            return xml

    def _formresult_to_xml(self, formresult):
        """returns a result dictionary as an xml mapping"""
        xml = ['<sourcedata>']
        for key, value in formresult.items():
            xml.append('<parameter key="%s">%s</parameter>' % 
                        (self._xml_escape(ustr(key)), self._xml_escape(ustr(value))))
        xml.append('</sourcedata>')
        return ''.join(xml)

    def _xml_escape(self, input):
        """entitize illegal chars in xml"""
        input = input.replace('&', '&amp;')
        input = input.replace('<', '&lt;')
        input = input.replace('>', '&gt;')
        input = input.replace('"', '&quot;')
        input = input.replace("'", '&apos;')
        return input

    def to_html(self, REQUEST=None, **kw):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """
        return ''

    def to_xml(self, REQUEST=None, **kw):
        """ Render the XML for this source.
        """
        return ''

    def is_cacheable(self, **kw):
        """ Specify the cacheability.
        """
        return self._is_cacheable

    def data_encoding(self):
        """ Specify the encoding of source's data.
        """
        return self._data_encoding

    def description(self):
        """ Specify the use of this source.
        """
        return self._description

    def get_title (self):
        return self.title

    def index_html(self, REQUEST=None, RESPONSE=None, view_method=None):
        """ render HTML with default or other test values in ZMI for
        purposes of testing the ExternalSource.
        """
        form = self.form()

        if REQUEST is not None and form:
            try:
                kw = form.validate_all(REQUEST)
            except (FormValidationError, ValidationError), err:
                # If we cannot validate (e.g. due to required parameters), 
                # return a form.
                # FIXME: How to get some feedback in the rendered page? E.g.
                # in case of validation errors.
                return form.render(REQUEST=REQUEST)
        else:
            kw = {}

        return self.to_html(REQUEST, **kw)

    # MODIFIERS

    security.declareProtected(ViewManagementScreens, 'set_form')
    def set_form(self, form):
        """ Set Formulator parameters form
        """
        self.parameters = form

    security.declareProtected(ViewManagementScreens, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        """ set encoding of data
        """
        self._data_encoding = encoding

    security.declareProtected(ViewManagementScreens, 'set_description')
    def set_description(self, desc):
        """ set description of external source's use
        """
        # If it is not unicode already, assume it is in the encoding as
        # specified by "management_page_charset".
        if type(desc) != type(u''):
            desc = unicode(desc, self.management_page_charset, 'replace')
        self._description = desc

    security.declareProtected(ViewManagementScreens, 'set_is_cacheable')
    def set_is_cacheable(self, cacheable):
        """ set cacheablility of source
        """
        self._is_cacheable = cacheable

InitializeClass(ExternalSource)
