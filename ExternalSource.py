# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
from interfaces import IExternalSource
# Zope
import Acquisition
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
# Silva
from Products.Silva.SilvaPermissions import ViewManagementScreens
# Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.Errors import ValidationError, FormValidationError

icon="www/silvaexternalsource.png"

class ExternalSource(Acquisition.Implicit):

    __implements__ = IExternalSource
    
    meta_type = "Silva External Source"

    security = ClassSecurityInfo()

    _data_encoding = 'ascii'

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.parameters = None        

    # ACCESSORS

    def form(self):
        """ get to the parameters form
        """
        return self.parameters

    def to_html(self, REQUEST, **kw):
        """ Render the HTML for inclusion in the render Silva HTML.
        """
        return ''

    def to_xml(self, REQUEST, **kw):
        """ Render the XML for this source.
        """
        return '<codesource> code source </codesource>'

    def is_cacheable(self, REQUEST, **kw):
        """ Specify the cacheability.
        """
        return 0

    def data_encoding(self):
        return self._data_encoding

    def index_html(self, REQUEST, RESPONSE):
        """ render HTML with default or other test values in ZMI for
        purposes of testing the ExternalSource.
        """
        form = self.form()

        try:
            kw = form.validate_all(REQUEST)
        except (FormValidationError, ValidationError), err:
            # If we cannot validate (e.g. due to required parameters), 
            # return a form.
            # FIXME: How to get some feedback in the rendered page? E.g.
            # in case of validation errors.
            return form.render(REQUEST=REQUEST)

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

InitializeClass(ExternalSource)
