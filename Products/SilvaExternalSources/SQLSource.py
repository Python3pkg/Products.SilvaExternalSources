# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import os

from five import grok
from zope.component import getMultiAdapter

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.Folder import Folder

from Products.ZSQLMethods.SQL import SQLConnectionIDs, SQL
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
# Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens, \
    AccessContentsInformation
from Products.Silva.helpers import add_and_edit
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.ExternalSource import EditableExternalSource

from silva.core import conf as silvaconf
from silva.core.interfaces import IVersion
from silva.core.services.base import ZMIObject
from zeam.utils.batch import Batch, IBatching

DATA_PATH = os.path.join(os.path.dirname(__file__), 'layout')


class SQLSource(EditableExternalSource, Folder, ZMIObject):
    grok.implements(IExternalSource)
    # register icon and factories
    silvaconf.icon('www/sqlsource.png')
    silvaconf.factory('manage_addSQLSourceForm')
    silvaconf.factory('manage_addSQLSource')
    silvaconf.zmi_addable(True)

    meta_type = "Silva SQL Source"
    security = ClassSecurityInfo()

    _sql_method_id = 'sql_method'
    _layout_id = 'layout'
    _default_batch_size = 10
    _v_cached_parameters = None

    # ZMI Tabs
    manage_options = (
        {'label':'Edit', 'action':'editSQLSource'},
        {'label':'Parameters', 'action':'parameters/manage_main'},
        ) + Folder.manage_options
    management_page_charset = 'utf-8'

    security.declareProtected(ViewManagementScreens, 'editSQLSource')
    editSQLSource = PageTemplateFile(
        'www/sqlSourceEdit', globals(),  __name__='sqlCodeSource')

    def __init__(self, id):
        self.id = id
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
    def to_html(self, content, request, **parameters):
        """ render HTML for SQL source
        """
        values = self._get_data(parameters)
        names = values.names()
        batch_size = self._default_batch_size
        if parameters.get('sqlbatchsize'):
            batch_size = int(parameters.get('sqlbatchsize'))
        data = Batch(
            values.dictionaries(),
            factory=self._decode_dict_helper,
            count=batch_size,
            name=self.getId(),
            request=request)
        model = content
        if IVersion.providedBy(content):
            model = content.get_content()
        layout = self._getOb(self._layout_id)
        batch = getMultiAdapter((model, data, request), IBatching)()
        return layout(
            table=data, batch=batch, names=names, parameters=parameters)

    def _get_data(self, args):
        if not self._sql_method:
            self._set_sql_method()
        elif self._v_cached_parameters != self.get_parameters_form().get_field_ids():
            self._set_sql_method()
        args = self._encode_dict_helper(args)
        return self._sql_method(REQUEST=args)

    def _decode_dict_helper(self, dictionary):
        for key, value in list(dictionary.items()):
            if type(value) is type(''):
                dictionary[key] = str(
                    value, self._data_encoding, 'replace')
        return dictionary

    def _encode_dict_helper(self, dictionary):
        for key, value in list(dictionary.items()):
            if type(value) is type(''):
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
        self._v_cached_parameters = parameters = self.get_parameters_form().get_field_ids()
        arguments = '\n'.join(parameters)
        self._sql_method = SQL(
            self._sql_method_id, '', self._connection_id,
            arguments.encode('ascii'), self._statement.encode('UTF-8'))
        self._p_changed = 1

    # MANAGERS

    security.declareProtected(ViewManagementScreens, 'manage_editSQLSource')
    def manage_editSQLSource(
        self, title, data_encoding, statement, connection_id=None,
        description=None, cacheable=None, layout_id=None, reset_layout=None,
        reset_params=None, previewable=None, usable=None,
        ):
        """ Edit SQLSource object
        """
        msg = ''

        if reset_layout:
            reset_table_layout(self)
            return self.editSQLSource(
                manage_tabs_message="Table rendering pagetemplate reset " \
                    "to default layout.")

        if reset_params:
            reset_parameter_form(self)
            return self.editSQLSource(
                manage_tabs_message="Parameters form reset to default.")

        if data_encoding and data_encoding != self._data_encoding:
            try:
                str('abcd', data_encoding, 'replace')
            except LookupError:
                # unknown encoding, return error message
                msg  += "Unknown encoding %s, not changed!" % data_encoding
                return self.editSQLSource(manage_tabs_message=msg)
            self.set_data_encoding(data_encoding)
            msg += "Data encoding changed. "

        if connection_id and connection_id != self._connection_id:
            self._set_connection_id(connection_id)
            msg += "Connection id changed. "

        if statement:
            statement = str(statement, 'UTF-8')
            self._set_statement(statement)
            msg += "SQL statement changed. "

        title = str(title, self.management_page_charset)
        if title and title != self.title:
            self.set_title(title)
            msg += "Title changed. "

        description = str(description, self.management_page_charset)
        if description != self._description:
            self.set_description(description)
            msg += "Description changed. "

        if not bool(cacheable) is self.is_cacheable():
            self.set_cacheable(bool(cacheable))
            msg += "Cacheability setting changed. "

        if not bool(previewable) is self.is_previewable():
            self.set_previewable(bool(previewable))
            msg += "Previewable setting changed. "

        if not bool(usable) is self.is_usable():
            self.set_usable(bool(usable))
            msg += "Usability setting changed. "

        if layout_id and layout_id != self._layout_id:
            self._layout_id = layout_id
            msg += "Layout object id changed. "

        return self.editSQLSource(manage_tabs_message=msg)

InitializeClass(SQLSource)


manage_addSQLSourceForm = PageTemplateFile(
    "www/sqlSourceAdd", globals(), __name__='manage_addSQLSourceForm')

def manage_addSQLSource(context, id, title=None, REQUEST=None):
    """Add a SQLSource object
    """
    source = SQLSource(id)
    title = str(title, source.management_page_charset)
    source.title = title
    context._setObject(id, source)
    source = context._getOb(id)
    source._set_statement('SELECT <dtml-var columns> FROM <dtml-var table>')
    # parameters form
    reset_parameter_form(source)
    reset_table_layout(source)
    add_and_edit(context, id, REQUEST, screen='editSQLSource')
    return ''

def reset_table_layout(source):
    # Works for Zope object implementing a 'write()" method...
    layout = [
        ('layout', ZopePageTemplate, 'sqltable.zpt'),
    ]

    for identifier, factory, filename in layout:
        with open(os.path.join(DATA_PATH, filename), 'rb') as data:
            if identifier not in source.objectIds():
                source._setObject(identifier, factory(identifier))
            source._getOb(identifier).write(data.read())

def reset_parameter_form(source):
    with open(os.path.join(DATA_PATH, 'sqlparameters.xml')) as data:
        form = ZMIForm('form', 'Parameters form', unicode_mode=1)
        XMLToForm(data.read(), form)
        source.set_form(form)
