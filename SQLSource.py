# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
from interfaces import IExternalSource
from ExternalSource import ExternalSource
# Zope
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from Products.ZSQLMethods.SQL import SQLConnectionIDs, SQL
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
# Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle

icon="www/silvasqldatasource.png"

class SQLSource(SimpleItem, ExternalSource):
    __implements__ = IExternalSource
    
    meta_type = "Silva SQL Source"

    security = ClassSecurityInfo()

    _sql_method_id = 'sql_method'
    _v_cached_parameters = None

    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editSQLSource'},
        {'label':'Parameters', 'action':'parameters/manage_main'},
        {'label':'Layout', 'action':'layout/manage_main'},
        {'label':'View', 'action':'index_html'},
        ) + SimpleItem.manage_options

    security.declareProtected(ViewManagementScreens, 'sqlSourceEdit')    
    editSQLSource = PageTemplateFile(
        'www/sqlSourceEdit', globals(),  __name__='sqlCodeSource')

    manage_main = editSQLSource

    def __init__(self, id, title):
        SQLSource.inheritedAttribute('__init__')(self, id, title)
        self._sql_method = None
        self._statement = None
        self._connection_id = None
        self.layout = None

    # ACCESSORS
   
    def connection_id(self):
        return self._connection_id
    
    def statement(self):
        return self._statement

    def available_connection_ids(self):
        return SQLConnectionIDs(self)

    def to_html(self, REQUEST, **kw):
        """ render HTML for SQL source
        """
        q = {}
        q.update(REQUEST)
        q.update(kw)
        
        brains = self._get_data(q)
        return self.layout(
            table=self._table_helper(brains), parameters=kw)

    def _table_helper(self, brains):
        # make cell data unicode strings
        enc = self._data_encoding
        table = {}
        table['names'] = [unicode(name, enc, 'replace') for name in brains.names()]
        table['rows'] = []
        for row in brains:            
            cells = []
            table['rows'].append(cells)
            for cell in row:
                if cell is None:
                    celldata = u''
                elif type(cell) is type(''):
                    celldata = unicode(cell, enc, 'replace')
                else:
                    celldata = unicode(str(cell), enc, 'replace')
                cells.append(celldata)
        return table

    #def to_xml(self, REQUEST, **kw):        

    def _get_data(self, args):
        if not self._sql_method:
            self._set_sql_method()
        elif self._v_cached_parameters != self.form().get_field_ids():
            self._set_sql_method()
        return self._sql_method(REQUEST=args)

    # MODIFIERS

    def _set_statement(self, statement):
        self._statement = statement
        #invalidate sql method
        self._sql_method = None
        self._p_changed = 1

    def _set_connection_id(self, id):
        self._connection_id = id
        #invalidate sql method
        self._sql_method = None
        self._p_changed = 1
        
    def _set_sql_method(self):
        self._v_cached_parameters = parameters = self.form().get_field_ids()
        arguments = '\n'.join(parameters)
        self._sql_method = SQL(
            self._sql_method_id, '', self._connection_id, 
            arguments.encode('ascii'), self._statement.encode('ascii'))
        self._p_changed = 1

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editSQLSource')
    def manage_editSQLSource(
        self, title, connection_id, data_encoding, statement, 
        description=None, reset_layout=None, reset_params=None):
        """ Edit SQLSource object
        """
        msg = ''
        if title and title != self.title:
            self.title = title
            msg += 'Title changed. '

        if connection_id and connection_id != self._connection_id:
            self._set_connection_id(connection_id)
            msg += 'Connection id changed. '

        if statement and statement != self._statement:
            self._set_statement(statement)
            msg += 'SQL statement changed. '

        if data_encoding and data_encoding != self._data_encoding:
            self.set_data_encoding(data_encoding)
            msg += 'Data encoding changed. '

        if description and description != self._description:
            self.set_description(description)
            msg += 'Description changed. '

        if reset_layout:
            reset_table_pagetemplate(self)
            msg += 'Table rendering pagetemplate reset to default layout. '

        if reset_params:
            reset_parameter_form(self)
            msg += 'Parameters form reset to default. '

        return self.editSQLSource(manage_tabs_message=msg)

InitializeClass(SQLSource)

addSQLSource = PageTemplateFile(
    "www/sqlSourceAdd", globals(), __name__='addSQLSource')

import os

def reset_table_pagetemplate(sqlsource):
    filename = os.path.join(package_home(globals()), 'layout', 'table.zpt')
    f = open(filename, 'rb')
    sqlsource.layout = ZopePageTemplate('layout', f.read())
    f.close()    

def reset_parameter_form(sqlsource):
    filename = os.path.join(package_home(globals()), 'layout', 'parameters.xml')
    f = open(filename, 'rb')
    form = ZMIForm('form', 'Parameters form')
    XMLToForm(f.read(), form)
    f.close()
    sqlsource.set_form(form)

def manage_addSQLSource(context, id, title, REQUEST=None):
    """Add a SQLSource object
    """
    datasource = SQLSource(id, title)
    context._setObject(id, datasource)
    datasource = context._getOb(id)
    datasource._set_statement('SELECT * FROM <dtml-var table>')
    # parameters form
    reset_parameter_form(datasource)
    # table rendering layout pagetemplate
    reset_table_pagetemplate(datasource)
    add_and_edit(context, id, REQUEST)
    return datasource
