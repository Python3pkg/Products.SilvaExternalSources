# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.35 $
from interfaces import IExternalSource
from ExternalSource import ExternalSource

from zope.interface import implements

# Zope
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.interfaces import IAsset

# I18N stuff
from Products.Silva.i18n import translate as _



icon="www/csvsource.png"
addable_priority = 1.8

import ASV

class CSVSource(ExternalSource, SilvaObject, Folder):

    """CSV Source is an asset that displays tabular data from a 
    spreadsheet or database. The format of the uploaded text file
    should be &#8216;comma separated values&#8217;. The asset can 
    be linked directly, or inserted in a document with the External 
    Source element. If necessary, all aspects of the display can be
    customized in the rendering templates of the CSV Source.
    """


    implements(IExternalSource, IAsset)
    
    meta_type = "Silva CSV Source"

    management_page_charset = 'utf-8'

    security = ClassSecurityInfo()
    
    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCSVSource'},
        {'label':'Edit Data', 'action':'editDataCSVSource'},
        ) + Folder.manage_options

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'editCSVSource')    
    editCSVSource = PageTemplateFile(
        'www/csvSourceEdit', globals(),  __name__='editCSVSource')

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'editDataCSVSource')    
    editDataCSVSource = PageTemplateFile(
        'www/csvSourceEditData', globals(),  __name__='editCSVSourceData')


    _layout_id = 'layout'

    _default_batch_size = 20

    def __init__(self, id, title, file):
        CSVSource.inheritedAttribute('__init__')(self, id, '')
        self._raw_data = None
        self._data = []
        if file is not None:
            self.update_data(file.read())
        else:
            self.update_data("")
        return

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 'raw_data')
    def raw_data (self):
        if type(self._raw_data) != type(u''):
            data = unicode(self._raw_data, self._data_encoding, 'replace')
        else:
            data = self._raw_data
        return data

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 'to_html')
    def to_html(self, *args, **kw):
        """ render HTML for CSV source
        """
        layout = self[self._layout_id]
        rows = self._data[:]
        param = {}
        param.update(kw)
        if not param.get('csvtableclass'):
            param['csvtableclass'] = 'default'
        if param.get('csvbatchsize'):
            bs = int(param.get('csvbatchsize'))
            param['csvbatchsize'] = bs
        else:
            param['csvbatchsize'] = CSVSource._default_batch_size
        if rows:
            headings = rows[0]
            rows = rows[1:]
            param['headings'] = headings
        return layout(table=rows, parameters=param)

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title (self):
        """Return meta-data title for this instance
        """
        ms = self.service_metadata
        return ms.getMetadataValue(self, 'silva-content', 'maintitle')

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'get_table_class')
    def get_table_class (self):
        """Returns css class for table """
        return self._table_class
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation, 'description')
    def description (self):
        """ Return desc from meta-data system"""
        ms = self.service_metadata
        return ms.getMetadataValue(self, 'silva-extra', 'content_description')

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'update_data')
    def update_data (self, data):
        asv = ASV.ASV()
        asv.input(data, ASV.CSV(), has_field_names=0)
        # extracting the raw data out of the asv structure
        # thereby converting them into plain list-of-lists
        # containing strings
        rows = []
        for r in asv:
            l = []
            for c in r:
                l.append(c)
            rows.append(l)
        # convert the data to unicode
        rows = self._unicode_helper(rows)
        self._data = rows
        self._raw_data = data
        return

    def _unicode_helper(self, rows):
        for r in rows:
            for i in xrange(len(r)):
                value = r[i]
                if type(value) is type(''):
                    r[i] = unicode(value, self._data_encoding, 'replace')
        return rows


    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_data_encoding')
    def set_data_encoding (self, encoding):
        self._data_encoding = encoding
        self.update_data(self._raw_data)
        return

##     security.declareProtected(ViewManagementScreens, 'set_headings')
##     def set_headings (self, headings):
##         self._has_headings = (not not headings)
##         return

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_table_class')
    def set_table_class (self, css_class):
        self._table_class = css_class
        return 

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_title')
    def set_title (self, title):
        CSVSource.inheritedAttribute('set_title')(self, title)
        return

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_description')
    def set_description(self, desc):
        t = type(desc)
        if t == type(u''):
            desc = desc.encode('utf-8')
        # Since the metadata system will re-validate, it cannot
        # accept unicode... ugh... so, re-encode to utf-8 first.
        ms = self.service_metadata
        binding = ms.getMetadata(self)
        d = {'content_description' : desc}
        binding.setValues('silva-extra', d)
        pass

    # MANAGERS

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editCSVSource')
    def manage_editCSVSource(
        self, title, character_set, description=None, cacheable=None,
        headings=None, file=None):
        """ Edit CSVSource object
        """
        msg = u''
        charset = character_set
        # first check if encoding is known
        # if not, don't change it and display error message
        try:
            unicode('abcd', charset, 'replace')
        except LookupError:
            # unknown encoding, return error message
            m = _("Unknown encoding ${enc}, not changed! ")
            m.set_mapping({"enc":charset})
            msg += m #"Unknown encoding %s, not changed!. " % charset
            return self.editCSVSource(manage_tabs_message=msg)
        self.set_data_encoding(charset)
        m = _("Data encoding changed to: ${enc}. ")
        m.set_mapping({"enc":charset})
        msg += m #'Data encoding changed to: %s. ' % charset

        # Assume title is in the encoding as specified 
        # by "management_page_charset". Store it in unicode.
        title = unicode(
            title, self.management_page_charset)
        
        if title and title != self.title:
            self.set_title(title)
            m = _("Title changed. ")
            msg += m #'Title changed. '
            
        # Assume description is in the encoding as specified 
        # by "management_page_charset". Store it in unicode.
        description = unicode(
            description, self.management_page_charset, 'replace')
            
        if description and description != self._description:
            self.set_description(description)
            m = _("Description changed. ")
            msg += m #'Description changed. '
        if not (not not cacheable) is (not not self._is_cacheable):
##             print 'cacheable', str(cacheable), str(self._is_cacheable)
            self.set_is_cacheable(cacheable)
            m = _("Cacheability setting changed. ")
            msg += m #'Cacheability setting changed. '
        if file:
            data = file.read()
            self.update_data(data)
            m = _("Data updated. ")
            msg += m #'Data updated. '
##         if not (not not headings) is (not not self._has_headings):
##             self._has_headings = (not not headings)
##             msg += 'Has headings setting changed. '
        return self.editCSVSource(manage_tabs_message=msg)

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editDataCSVSource')
    def manage_editDataCSVSource(self, data=None):
        """ Edit CSVSource raw data
        """
        if data:
            self.update_data(data)
            msg = _('Raw data updated. ')
        else:
            msg = u''
        return self.editDataCSVSource(manage_tabs_message=msg)

InitializeClass(CSVSource)

manage_addCSVSourceForm = PageTemplateFile(
    "www/csvSourceAdd", globals(), __name__='manage_addCSVSourceForm')

import os

def reset_parameter_form(csvsource):
    filename = os.path.join(package_home(globals()), 'layout', 'csvparameters.xml')
    f = open(filename, 'rb')
    form = ZMIForm('form', 'Parameters form', unicode_mode=1)
    XMLToForm(f.read(), form)
    f.close()
    csvsource.set_form(form)

def reset_table_layout(cs):
    # Works for Zope object implementing a 'write()" method...
    layout = [
        ('layout', ZopePageTemplate, 'csvtable.zpt'),
        ('macro', ZopePageTemplate, 'macro.zpt'),
    ]

    for id, klass, file in layout:
        filename = os.path.join(package_home(globals()), 'layout', file)
        f = open(filename, 'rb')
        if not id in cs.objectIds():
            cs._setObject(id, klass(id))
        cs[id].write(f.read())
        f.close()

def manage_addCSVSource(context, id, title, file=None, REQUEST=None):
    """Add a CSVSource object
    """
    cs = CSVSource(id, title, file)
    context._setObject(id, cs)
    cs = context._getOb(id)
    reset_table_layout(cs)
    reset_parameter_form(cs)
    # XXX
    # ZMI is assumed to be in utf-8
    if type(title) == type(''):
        title = unicode(title, 'utf-8', 'replace')
    cs.set_title(title)
    cs.set_description('CSV Source description')
    add_and_edit(context, id, REQUEST, screen='editCSVSource')
    return ''
