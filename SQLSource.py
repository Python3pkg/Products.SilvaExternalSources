# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
from interfaces import IExternalSource
from ExternalSource import ExternalSource
# Zope
from OFS.Folder import Folder
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from Products.ZSQLMethods.SQL import SQLConnectionIDs, SQL
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PythonScripts.PythonScript import PythonScript
# Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle

icon="www/silvasqldatasource.png"

class SQLSource(ExternalSource, Folder):

    __implements__ = IExternalSource
    
    meta_type = "Silva SQL Source"

    security = ClassSecurityInfo()

    _sql_method_id = 'sql_method'
    _layout_id = 'layout'
    _v_cached_parameters = None

    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editSQLSource'},
        {'label':'Parameters', 'action':'parameters/manage_main'},
        ) + Folder.manage_options

    security.declareProtected(ViewManagementScreens, 'sqlSourceEdit')    
    editSQLSource = PageTemplateFile(
        'www/sqlSourceEdit', globals(),  __name__='sqlCodeSource')

    def __init__(self, id, title):
        SQLSource.inheritedAttribute('__init__')(self, id, title)
        self._sql_method = None
        self._statement = None
        self._connection_id = None

    # ACCESSORS

    def layout_id(self):
        return self._layout_id

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
        # We don't need to pass in the request explicitly (how would I do
        # that anyway) since we're calling the layout (e.g. a ZPT or Python-
        # Script) which can get to the request itself.
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
                if type(cell) is type(''):
                    celldata = unicode(cell, enc, 'replace')
                else:
                    celldata = cell
                cells.append(celldata)
        return table

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
        description=None, cacheable=None, layout_id=None, reset_layout=None,
        reset_params=None
        ):
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

        if not (not not cacheable) is (not not self._is_cacheable):
            self.set_is_cacheable(cacheable)
            msg += 'Cacheability setting changed. '

        if layout_id and layout_id != self._layout_id:
            self._layout_id = layout_id
            msg += 'Layout object id changed. '

        if reset_layout:
            reset_table_layout(self)
            msg += 'Table rendering pagetemplate reset to default layout. '

        if reset_params:
            reset_parameter_form(self)
            msg += 'Parameters form reset to default. '

        return self.editSQLSource(manage_tabs_message=msg)

InitializeClass(SQLSource)

addSQLSource = PageTemplateFile(
    "www/sqlSourceAdd", globals(), __name__='addSQLSource')

import os

def reset_table_layout(sqlsource):
    # Works for Zope object implementing a 'write()" method...
    layout = [
        ('layout', ZopePageTemplate, 'table.zpt'),
        ('macro', ZopePageTemplate, 'macro.zpt'),
    ]

    for id, klass, file in layout:
        filename = os.path.join(package_home(globals()), 'layout', file)
        f = open(filename, 'rb')
        if not id in sqlsource.objectIds():
            sqlsource._setObject(id, klass(id))
        sqlsource[id].write(f.read())
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
    datasource._set_statement('SELECT <dtml-var columns> FROM <dtml-var table>')
    # parameters form
    reset_parameter_form(datasource)
    # table rendering layout pagetemplate
    reset_table_layout(datasource)
    add_and_edit(context, id, REQUEST, screen='editSQLSource')
    return ''