# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.20 $
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
from Products.Silva.SilvaPermissions import ViewManagementScreens, AccessContentsInformation
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle


# I18N stuff
from Products.Silva.i18n import translate as _


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

    security.declareProtected(AccessContentsInformation, 'to_html')
    def to_html(self, REQUEST, **kw):
        """ render HTML for SQL source
        """
        brains = self._get_data(kw)
        names = brains.names()
        layout = self[self._layout_id]
        # XXX: we're materializing all data in the resultset here which
        # hurts performance for large sets. Brains 'normally' lazily
        # retrieve the data, but then we need to decode to unicode in
        # the wrong - i.e. in the ZPT's - layer...
        #
        # We need a better way.
        #
        data = [self._decode_dict_helper(d) for d in brains.dictionaries()]
        # We don't need to pass in the request explicitly (how would I do
        # that anyway) since we're calling the layout (e.g. a ZPT or Python
        # Script) which can get to the request itself.        
        return layout(table=data, names=names, parameters=kw)

    def _get_data(self, args):
        if not self._sql_method:
            self._set_sql_method()
        elif self._v_cached_parameters != self.form().get_field_ids():
            self._set_sql_method()
        args = self._encode_dict_helper(args)
        return self._sql_method(REQUEST=args)

    def _decode_dict_helper(self, dictionary):
        for key, value in dictionary.items():
            if type(value) is type(''):
                dictionary[key] = unicode(
                    value, self._data_encoding, 'replace')
        return dictionary
    
    def _encode_dict_helper(self, dictionary):
        for key, value in dictionary.items():
            if type(value) is type(u''):
                dictionary[key] =  value.encode(
                    self._data_encoding, 'replace')
        return dictionary

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
        msg = u''

        if data_encoding and data_encoding != self._data_encoding:
            try:
                unicode('abcd', data_encoding, 'replace')
            except LookupError:
                # unknown encoding, return error message
                m = _("Unknown encoding ${enc}, not changed! ")
                m.set_mapping({"enc":charset})
                sm = unicode(m)
                msg += sm #"Unknown encoding %s, not changed!. " % data_encoding
                return self.editSQLSource(manage_tabs_message=msg)
            self.set_data_encoding(data_encoding)
            m = _("Data encoding changed. ")
            sm = unicode(m)
            msg += sm #'Data encoding changed. '

        if title and title != self.title:
            self.title = title
            m = _("Title changed. ")
            sm = unicode(m)
            msg += sm #'Title changed. '

        if connection_id and connection_id != self._connection_id:
            self._set_connection_id(connection_id)
            m = _("Connection id changed. ")
            sm = unicode(m)
            msg += sm #'Connection id changed. '

        if statement and statement != self._statement:
            self._set_statement(statement)
            m = _("SQL statement changed. ")
            sm = unicode(m)
            msg += sm #'SQL statement changed. '

        # Assume description is in the encoding as specified 
        # by "management_page_charset". Store it in unicode.
        description = unicode(
            description, self.management_page_charset, 'replace')
            
        if description != self._description:
            self.set_description(description)
            m = _("Description changed. ")
            sm = unicode(m)
            msg += sm #'Description changed. '

        if not (not not cacheable) is (not not self._is_cacheable):
            self.set_is_cacheable(cacheable)
            m = _("Cacheability setting changed. ")
            sm = unicode(m)
            msg += sm #'Cacheability setting changed. '

        if layout_id and layout_id != self._layout_id:
            self._layout_id = layout_id
            m = _("Layout object id changed. ")
            sm = unicode(m)
            msg += sm #'Layout object id changed. '

        if reset_layout:
            reset_table_layout(self)
            m = _("Table rendering pagetemplate reset to default layout. ")
            sm = unicode(m)
            msg += sm #'Table rendering pagetemplate reset to default layout. '

        if reset_params:
            reset_parameter_form(self)
            m = _("Parameters form reset to default. ")
            sm = unicode(m)
            msg += sm #'Parameters form reset to default. '

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
