# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.31 $

from zope.interface import implements
# Zope
import Acquisition
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
# Silva
from Products.Silva import SilvaPermissions
# Interfaces
from Products.Silva.interfaces import IRoot
from Products.SilvaExternalSources.interfaces import IExternalSource
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
                if IExternalSource.providedBy(obj):
                    if not sources.has_key(obj.id):
                        sources[obj.id] = obj
            if IRoot.providedBy(context):
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
    if IExternalSource.providedBy(nearest):
        return nearest    
    if IRoot.providedBy(context):
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

    implements(IExternalSource)
    
    meta_type = "Silva External Source"

    security = ClassSecurityInfo()

    management_page_charset = 'utf-8'
    
    # Cannot make it 'private'; the form won't work in the ZMI if it was.
    parameters = None 

    _data_encoding = 'ISO-8859-15'
    _description = ''
    _is_cacheable = 0

    # XXX ExternalSource is never used directly, it serves as BaseClass or
    # Mixin. As such, I don't think it should have this fairly meanless __init__
    def __init__(self, id, title):
        self.id = id
        self.title = title

    # ACCESSORS

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                                'form')
    def form(self):
        """ get to the parameters form
        """
        return self.parameters

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 
                                'get_rendered_form_for_editor')
    def get_rendered_form_for_editor(self, REQUEST=None):
        """return the rendered form"""
        # XXX this is never triggered AFAIK, because kupu sets a 'null'
        # string, and not a value that resolves to False
        if REQUEST.has_key('docref') and REQUEST['docref']:
            REQUEST.form['model'] = self.resolve_ref(REQUEST['docref'])
        else:
            # buggy behaviour. but allows backward compatibility
            REQUEST.form['model'] = self
        xml = ['<?xml version="1.0" encoding="UTF-8" ?>\n',
                '<form action="" method="POST">',
                ('<input type="hidden" name="metatype" value="%s" />' % 
                        self.meta_type),
                ('<table width="100%" id="extsourceform" '
                        'style="display: block" class="plain">')]
        for field in self.form().get_fields():
            xml.append('<tr><td>%s</td>' % field.title())
            value = None
            if REQUEST.form.has_key(field.id):
                value = REQUEST.form[field.id]
            if value is None:
                # default value (if available)
                value = field.get_value('default')
            xml.append('<td>%s</td></tr>' % 
                            (field.render(ustr(value, 'UTF-8'))))
        xml.append('</table></form>')
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
        form = self.form()
        try:
            result = form.validate_all(REQUEST)
        except FormValidationError, e:
            REQUEST.RESPONSE.setStatus(400, 'Bad Request')
            return '&'.join(['%s=%s' % (e.field['title'], e.error_text) 
                                for e in e.errors])
        else:
            REQUEST.RESPONSE.setHeader('Content-Type', 
                                        'text/xml;charset=UTF-8');
            result['metatype'] = self.meta_type
            xml = self._formresult_to_xml(result)
            return xml

    def _formresult_to_xml(self, formresult):
        """returns a result dictionary as an xml mapping"""
        xml = ['<sourcedata>']
        for key, value in formresult.items():
            xml.append('<parameter key="%s">%s</parameter>' % 
                        (self._xml_escape(ustr(key)), 
                            self._xml_escape(ustr(value))))
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 
                                'to_html')
    def to_html(self, REQUEST=None, **kw):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """
        return ''

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 
                                'to_xml')
    def to_xml(self, REQUEST=None, **kw):
        """ Render the XML for this source.
        """
        return ''

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 
                                'is_cacheable')
    def is_cacheable(self, **kw):
        """ Specify the cacheability.
        """
        return self._is_cacheable

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

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 
                                'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None, view_method=None):
        """ render HTML with default or other test values in ZMI for
        purposes of testing the ExternalSource.
        """
        form = self.form()
        if REQUEST is not None and form:
            if not hasattr(REQUEST, 'model'):
                REQUEST.model = self
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

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
                                'set_form')
    def set_form(self, form):
        """ Set Formulator parameters form
        """
        self.parameters = form

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
                                'set_data_encoding')
    def set_data_encoding(self, encoding):
        """ set encoding of data
        """
        self._data_encoding = encoding

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
                                'set_description')
    def set_description(self, desc):
        """ set description of external source's use
        """
        self._description = desc

    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
                                'set_is_cacheable')
    def set_is_cacheable(self, cacheable):
        """ set cacheablility of source
        """
        self._is_cacheable = cacheable

InitializeClass(ExternalSource)
