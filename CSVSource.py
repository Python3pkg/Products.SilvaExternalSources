# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
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

icon="www/codesource.png"

import ASV

class CSVSource(ExternalSource, Folder):

    __implements__ = IExternalSource
    
    meta_type = "Silva CSV Source"

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

    def __init__(self, id, title, file):
        CSVSource.inheritedAttribute('__init__')(self, id, title)
        self._raw_data = None
        self._data = []
        self._has_headings = CSVSource._has_headings
        self.update_data(file.read())
        return

    # ACCESSORS

    def has_headings (self):
        return self._has_headings

    def raw_data (self):
        return self._raw_data

    def to_html(self, REQUEST, **kw):
        """ render HTML for CSV source
        """
        layout = self[self._layout_id]
        rows = self._unicode_helper(self._data)
        if self._has_headings:
            headings = rows[0]
            rows = rows[1:]
        else:
            headings = None
        return layout(table=rows, headings=headings, parameters=kw)

    def _unicode_helper(self, rows):
        for r in rows:
            for i in xrange(len(r)):
                value = r[i]
                if type(value) is type(''):
                    r[i] = unicode(value, self._data_encoding, 'replace')
        return rows

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
        self._data = rows
        self._raw_data = data
        return

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editCSVSource')
    def manage_editCSVSource(
        self, title, data_encoding, description=None, cacheable=None,
        headings=None, file=None):
        """ Edit CSVSource object
        """
        msg = ''
        if title and title != self.title:
            self.title = title
            msg += 'Title changed. '
        if data_encoding and data_encoding != self._data_encoding:
            self.set_data_encoding(data_encoding)
            msg += 'Data encoding changed. '
        if description and description != self._description:
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

addCSVSource = PageTemplateFile(
    "www/csvSourceAdd", globals(), __name__='addCSVSource')

import os

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


def manage_addCSVSource(context, id, title, file, REQUEST=None):
    """Add a CSVSource object
    """
    cs = CSVSource(id, title, file)
    context._setObject(id, cs)
    cs = context._getOb(id)
    reset_table_layout(cs)
    add_and_edit(context, id, REQUEST, screen='editCSVSource')
    return ''
