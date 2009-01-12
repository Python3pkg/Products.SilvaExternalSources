# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

#for the traceback info
import sys
from urllib import quote

from zope.interface import implements
from DocumentTemplate import sequence
# Zope
import Acquisition
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.i18n import translate as _
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
        
        Only lists sources that can be reached from the context 
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
        return sequence.sort(sources.items(), (('title', 'nocase', 'asc'),))

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
        if REQUEST.has_key('docref') and REQUEST['docref']:
            # need to quote the docref, as resolve_ref
            #(actually OFS.CopySupport._cb_decode) unquotes it
            REQUEST.form['model'] = self.resolve_ref(quote(REQUEST['docref']))
        else:
            # buggy behaviour. but allows backward compatibility
            REQUEST.form['model'] = self
        xml = ['<?xml version="1.0" encoding="UTF-8" ?>\n',
                '<form id="extsourceform" action="" method="POST">\r',
                ('<input type="hidden" name="metatype" value="%s" />\n' % 
                        self.meta_type),
                ('<table width="100%" id="extsourceform" cellpadding="0" cellspacing="0" '
                        '>\n<tbody>\n')]

        form = REQUEST.form.copy()
        formcopy = {} 
        # pfff... what's that, not allowed to change a dict during iteration?!? ;)
        for k, v in form.iteritems():
            vtype = 'string'
            if '__type__' in k:
                k, vtype = k.split('__type__')
            formcopy[k] = v

        for field in self.form().get_fields():
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
				
            xml.append('<tr>\n<td width="7em" style="vertical-align: top"><a href="#" onclick="return false" %s>%s%s</a></td>\n' % (
                fieldCssClasses, fieldDescription, ustr(field.values['title'], 'UTF-8'))
                )

            value = None
            #the field id is actually _always_ lowercase in formcopy
            # (see https://bugs.launchpad.net/silva/+bug/180860)
            if formcopy.has_key(field.id.lower()):
                value = formcopy[field.id.lower()]
            if value is None:
                # default value (if available)
                value = field.get_value('default')
            if type(value) == list:
                value = [ustr(self._xml_unescape(x), 'UTF-8') for x in value]
            elif field.meta_type == "CheckBoxField":
                value = int(value)
            else:
                value = ustr(self._xml_unescape(value), 'UTF-8')
            xml.append('<td>%s</td>\n</tr>\n' % 
                            (field.render(value)))

        # if a Code Source has no parameters, inform the user how to proceed
        if len(self.form().get_fields()) == 0:
            no_params = _('This Code Source has no adjustable settings. Click a button to insert or remove it.')
            xml.append('<tr>\n<td>%s</td>\n</tr>\n' % no_params)

        xml.append('</tbody>\n</table>\n</form>\n')
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
        if REQUEST.has_key('docref') and REQUEST['docref']:
            # need to quote the docref, as resolve_ref
            #(actually OFS.CopySupport._cb_decode) unquotes it
            REQUEST.form['model'] = self.resolve_ref(quote(REQUEST['docref']))
        else:
            # buggy behaviour. but allows backward compatibility
            REQUEST.form['model'] = self
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
            xml = self._formresult_to_xml(result)
            return xml

    def _formresult_to_xml(self, formresult):
        """returns a result dictionary as an xml mapping"""
        xml = ['<sourcedata>','<sourceinfo>']
        xml.append('<metatype>%s</metatype>'%self.meta_type)
        xml.append('<source_id>%s</source_id>'%self.id)
        xml.append('<source_title>%s</source_title>'%self._xml_escape(ustr(self.get_title())))
        xml.append('<source_desc>%s</source_desc>'%self._xml_escape(ustr(self.description())))
        xml.append('</sourceinfo>')
        xml.append('<params>')
        for key, value in formresult.items():
            t = type(value).__name__
            xml.append('<parameter type="%s" id="%s">%s</parameter>' % 
                        (t, self._xml_escape(ustr(key)), 
                            self._xml_escape(ustr(value))))
        xml.append('</params>')
        xml.append('</sourcedata>')
        return ''.join(xml)

    def _xml_escape(self, input):
        """entitize illegal chars in xml"""
        input = input.replace('&', '&amp;')
        input = input.replace('<', '&lt;')
        input = input.replace('>', '&gt;')
        return input

    def _xml_unescape(self, input):
        """entitize illegal chars in xml"""
        input = input.replace('&amp;', '&')
        input = input.replace('&lt;', '<')
        input = input.replace('&gt;', '>')
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

    """If the external source errors out, log the traceback to the zope error log.
       This function allows continues processing"""
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'log_traceback')
    def log_traceback(self):
        error_log = self.error_log
        url = error_log.raising( sys.exc_info() )

InitializeClass(ExternalSource)
