# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.9 $
from interfaces import IExternalSource
from ExternalSource import ExternalSource
# Zope
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.Formulator.Form import ZMIForm
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.Silva.helpers import add_and_edit
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.interfaces import IAsset

icon="www/codesource.png"

import ASV

class CSVSource(ExternalSource, SilvaObject, Folder):

    """CSVSource is an ExternalSource which can display tabular data in
    'comma separated values' format.
    """


    __implements__ = IExternalSource, IAsset
    
    meta_type = "Silva CSV Source"

    management_page_charset = 'utf-8'

    security = ClassSecurityInfo()
    
    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editCSVSource'},
        {'label':'Edit Data', 'action':'editDataCSVSource'},
        ) + Folder.manage_options

    security.declareProtected(ViewManagementScreens, 'csvSourceEdit')    
    editCSVSource = PageTemplateFile(
        'www/csvSourceEdit', globals(),  __name__='editCSVSource')

    security.declareProtected(ViewManagementScreens, 'csvSourceEditData')    
    editDataCSVSource = PageTemplateFile(
        'www/csvSourceEditData', globals(),  __name__='editCSVSourceData')


    _layout_id = 'layout'

    _has_headings = 1
    _table_class = 'default'

    def __init__(self, id, title, file):
        CSVSource.inheritedAttribute('__init__')(self, id, '')
        self._raw_data = None
        self._data = []
        self._has_headings = CSVSource._has_headings
        if file is not None:
            self.update_data(file.read())
        else:
            self.update_data("")
        return

    # ACCESSORS

    def has_headings (self):
        return self._has_headings

    def raw_data (self):
        if type(self._raw_data) != type(u''):
            data = unicode(self._raw_data, self._data_encoding, 'replace')
        else:
            data = self._raw_data
        return data

    def to_html(self, REQUEST, **kw):
        """ render HTML for CSV source
        """
        layout = self[self._layout_id]
        rows = self._data[:]
        if rows and self._has_headings:
            headings = rows[0]
            rows = rows[1:]
        else:
            headings = None
	parameters = {}
	parameters.update(kw)
	parameters['table_class'] = self._table_class
        return layout(table=rows, headings=headings, parameters=parameters)

    def get_title (self):
        """Return meta-data title for this instance
        """
        ms = self.service_metadata
        return ms.getMetadataValue(self, 'silva-content', 'maintitle')

    security.declareProtected(ViewManagementScreens, 'get_table_class')
    def get_table_class (self):
        """Returns css class for table """
        return self._table_class
        
    def description (self):
        """ Return desc from meta-data system"""
        ms = self.service_metadata
        return ms.getMetadataValue(self, 'silva-extra', 'content_description')

    # MODIFIERS

    def update_data (self, data):
        asv = ASV.ASV()
        asv.input(data, ASV.CSV(), has_field_names=0)
        # extracting the raw data out of the asv structure
        rows = []
        for r in asv:
            l = []
            for c in r:
                l.append(c)
            rows.append(l)
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

    def set_data_encoding (self, encoding):
        self._data_encoding = encoding
        self.update_data(self._raw_data)
        return

    security.declareProtected(ViewManagementScreens, 'set_headings')
    def set_headings (self, headings):
        self._has_headings = (not not headings)
        return

    security.declareProtected(ViewManagementScreens, 'set_table_class')
    def set_table_class (self, css_class):
        self._table_class = css_class
        return 

    def set_title (self, title):
        CSVSource.inheritedAttribute('set_title')(self, title)
        return

    def set_description (self, desc ):
        t = type(desc)
        if t == type(u''):
            desc = desc.encode('utf-8')
        ms = self.service_metadata
        binding = ms.getMetadata(self)
        d = {'content_description' : desc}
        binding.setValues('silva-extra', d)
        pass

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editCSVSource')
    def manage_editCSVSource(
        self, title, character_set,  data_encoding, description=None, cacheable=None,
        headings=None, file=None):
        """ Edit CSVSource object
        """
        msg = ''
        if character_set == 'default' and data_encoding and data_encoding != self._data_encoding:
            charset = data_encoding
        else:
            charset = character_set
        # first check if encoding is known
        # if not, don't change it and display error message
        try:
            unicode('abcd', charset, 'replace')
        except LookupError:
            # unknown encoding, return error message
            msg += "Unknown encoding %s, not changed!. " % charset
            return self.editCSVSource(manage_tabs_message=msg)
        self.set_data_encoding(charset)
        msg += 'Data encoding changed to: %s. ' % charset
        
        if title and title != self.title:
            # XXX
            # ZMI is assumed to be in utf-8
            if type(title) == type(''):
                title = unicode(title, 'utf-8', 'replace')
            self.set_title(title)
            msg += 'Title changed. '
        if description and description != self._description:
            # XXX
            # ZMI is assumed to be in utf-8
            if type(description) == type(''):
                description = unicode(description, 'utf-8', 'replace')
            self.set_description(description)
            msg += 'Description changed. '
        if not (not not cacheable) is (not not self._is_cacheable):
            print 'cacheable', str(cacheable), str(self._is_cacheable)
            self.set_is_cacheable(cacheable)
            msg += 'Cacheability setting changed. '
        if file:
            data = file.read()
            self.update_data(data)
            msg += 'Data updated. '
        if not (not not headings) is (not not self._has_headings):
            self._has_headings = (not not headings)
            msg += 'Has headings setting changed. '
        return self.editCSVSource(manage_tabs_message=msg)

    security.declareProtected(ViewManagementScreens, 'manage_editDataCSVSource')
    def manage_editDataCSVSource(self, data=None):
        """ Edit CSVSource raw data
        """
        msg = ''
        if data and data != self._raw_data:
            self.update_data(data)
            msg += 'Raw data updated. '
        return self.editDataCSVSource(manage_tabs_message=msg)

InitializeClass(CSVSource)

manage_addCSVSourceForm = PageTemplateFile(
    "www/csvSourceAdd", globals(), __name__='manage_addCSVSourceForm')

import os

def reset_parameter_form(csvsource):
    filename = os.path.join(package_home(globals()), 'layout', 'csvparameters.xml')
    f = open(filename, 'rb')
    form = ZMIForm('form', 'Parameters form')
    XMLToForm(f.read(), form)
    f.close()
    csvsource.set_form(form)

def reset_table_layout(sqlsource):
    # Works for Zope object implementing a 'write()" method...
    layout = [
        ('layout', ZopePageTemplate, 'csvtable.zpt'),
        ('macro', ZopePageTemplate, 'csvmacro.zpt'),
    ]

    for id, klass, file in layout:
        filename = os.path.join(package_home(globals()), 'layout', file)
        f = open(filename, 'rb')
        if not id in sqlsource.objectIds():
            sqlsource._setObject(id, klass(id))
        sqlsource[id].write(f.read())
        f.close()


def manage_addCSVSource(context, id, title, file=None, REQUEST=None):
    """Add a CSVSource object
    """
    cs = CSVSource(id, title, file)
    context._setObject(id, cs)
    cs = context._getOb(id)
    reset_table_layout(cs)
    frm = ZMIForm('form', 'Empty Form')
    cs.set_form(frm)
##     reset_parameter_form(cs)
    # XXX
    # ZMI is assumed to be in utf-8
    if type(title) == type(''):
        title = unicode(title, 'utf-8', 'replace')
    cs.set_title(title)
    add_and_edit(context, id, REQUEST, screen='editCSVSource')
    return ''
