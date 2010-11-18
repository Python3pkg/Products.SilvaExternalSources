# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os

from five import grok
from zope.component import getUtility
from zope import schema
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching
from zope import component

# Zope
from AccessControl import ClassSecurityInfo
from App.Common import package_home
from App.class_init import InitializeClass
from OFS.Folder import Folder

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Asset import Asset
from Products.SilvaExternalSources import ASV
from Products.SilvaExternalSources.ExternalSource import EditableExternalSource
from Products.SilvaExternalSources.interfaces import ICSVSource
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core.interfaces import IVersion
from silva.core.views import views as silvaviews
from silva.core.conf import schema as silvaschema
from silva.core.conf.interfaces import ITitledContent
from silva.core import conf as silvaconf
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class CSVSource(Folder, EditableExternalSource, Asset):
    """CSV Source is an asset that displays tabular data from a
    spreadsheet or database. The format of the uploaded text file
    should be &#8216;comma separated values&#8217;. The asset can
    be linked directly, or inserted in a document with the External
    Source element. If necessary, all aspects of the display can be
    customized in the rendering templates of the CSV Source.
    """
    grok.implements(ICSVSource)

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

    # register priority, icon and factory
    silvaconf.priority(1)
    silvaconf.icon('www/csvsource.png')

    def __init__(self, id):
        super(CSVSource, self).__init__(id)
        self._raw_data = ''
        self._data = []

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_size')
    def get_file_size(self):
        """Get the size of the file as it will be downloaded.
        """
        if self._raw_data:
            return len(self._raw_data)
        return 0

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'raw_data')
    def raw_data(self):
        if type(self._raw_data) != type(u''):
            data = unicode(self._raw_data, self._data_encoding, 'replace')
        else:
            data = self._raw_data
        return data

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """ render HTML for CSV source
        """
        rows = self._data[:]
        param = {}
        param.update(parameters)
        if not param.get('csvtableclass'):
            param['csvtableclass'] = 'default'
        batch_size = self._default_batch_size
        batch_nav = ''
        if param.get('csvbatchsize'):
            batch_size = int(param.get('csvbatchsize'))
        model = content
        if IVersion.providedBy(content):
            model = content.get_content()
        if rows:
            headings = rows[0]
            rows = batch(
                rows[1:],
                count=batch_size, name=self.getId(), request=request)
            param['headings'] = headings
            batch_nav = component.getMultiAdapter(
                (model, rows, request), IBatching)()
        return self.layout(table=rows, batch=batch_nav, parameters=param)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Return meta-data title for this instance
        """
        ms = self.service_metadata
        return ms.getMetadataValue(self, 'silva-content', 'maintitle')

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'get_table_class')
    def get_table_class(self):
        """Returns css class for table """
        return self._table_class

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_description')
    def get_description(self):
        """ Return desc from meta-data system"""
        ms = self.service_metadata
        return ms.getMetadataValue(self, 'silva-extra', 'content_description')

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'update_data')
    def update_data(self, data):
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
        self.update_quota()

    def _unicode_helper(self, rows):
        for r in rows:
            for i in xrange(len(r)):
                value = r[i]
                if type(value) is type(''):
                    r[i] = unicode(value, self._data_encoding, 'replace')
        return rows

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file')
    def set_file(self, file):
        return self.update_data(file.read())

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        self._data_encoding = encoding
        self.update_data(self._raw_data)
        return

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_table_class')
    def set_table_class(self, css_class):
        self._table_class = css_class
        return

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_description')
    def set_description(self, desc):
        if not isinstance(desc, unicode):
            desc = desc.encode('utf-8')

        binding = getUtility(IMetadataService).getMetadata(self)
        binding.setValues('silva-extra', {'content_description' : desc})

    # MANAGERS

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editCSVSource')
    def manage_editCSVSource(
        self, title, character_set, description=None, cacheable=None,
        headings=None, file=None, previewable=None):
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
            m = _(
                "Unknown encoding ${enc}, not changed! ",
                mapping={"enc":charset})
            msg += m #"Unknown encoding %s, not changed!. " % charset
            return self.editCSVSource(manage_tabs_message=msg)
        self.set_data_encoding(charset)
        m = _(
            "Data encoding changed to: ${enc}. ",
            mapping={"enc":charset})
        msg += m #'Data encoding changed to: %s. ' % charset

        # Assume title is in the encoding as specified
        # by "management_page_charset". Store it in unicode.
        title = unicode(
            title, self.management_page_charset)

        if title and title != self.get_title():
            self.set_title(title)
            msg += _("Title changed. ")

        # Assume description is in the encoding as specified
        # by "management_page_charset". Store it in unicode.
        description = unicode(
            description, self.management_page_charset, 'replace')

        if description and description != self._description:
            self.set_description(description)
            m = _("Description changed. ")
            msg += m #'Description changed. '
        if not (not not cacheable) is (not not self._is_cacheable):
            self.set_cacheable(cacheable)
            m = _("Cacheability setting changed. ")
            msg += m #'Cacheability setting changed. '
        if not (not not previewable) is (not not self.is_previewable()):
            self.set_previewable(previewable)
            m = _("Previewable setting changed. ")
            msg += m #'Previewable setting changed. '
        if file:
            self.update_data(file.read())
            m = _("Data updated. ")
            msg += m #'Data updated. '
        return self.editCSVSource(manage_tabs_message=msg)

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editDataCSVSource')
    def manage_editDataCSVSource(self, data=None):
        """ Edit CSVSource raw data
        """
        msg = u''
        if data:
            self.update_data(data)
            msg = _('Raw data updated. ')
        return self.editDataCSVSource(manage_tabs_message=msg)


InitializeClass(CSVSource)


def reset_parameter_form(csvsource):
    filename = os.path.join(package_home(globals()),
                            'layout',
                            'csvparameters.xml')
    f = open(filename, 'rb')
    form = ZMIForm('form', 'Parameters form', unicode_mode=1)
    XMLToForm(f.read(), form)
    f.close()
    csvsource.set_form(form)

def reset_table_layout(cs):
    # Works for Zope object implementing a 'write()" method...
    layout = [
        ('layout', ZopePageTemplate, 'csvtable.zpt'),
    ]

    for id, factory, file in layout:
        filename = os.path.join(package_home(globals()), 'layout', file)
        f = open(filename, 'rb')
        if not id in cs.objectIds():
            cs._setObject(id, factory(id))
        cs[id].write(f.read())
        f.close()


@grok.subscribe(ICSVSource, IObjectCreatedEvent)
def source_created(source, event):
    reset_table_layout(source)
    reset_parameter_form(source)


@apply
def encoding_source():
    encodings = []
    for title, key in [
        ('ISO-8859-15 (Western Europe - Latin-1/EURO)', 'ISO-8859-15'),
        ('ISO-8859-1 (Western Europe - Latin-1)', 'ISO-8859-1'),
        ('Windows-1252 (Western Europe - Latin-1/Windows)', 'cp1252'),
        ('Mac Roman (Western Europe - Apple Macintosh)', 'mac_roman'),
        ('UTF-8 (Unicode)', 'utf-8')]:
        encodings.append(SimpleTerm(value=key, token=key, title=title))
    return SimpleVocabulary(encodings)


class ICSVSourceSchema(ITitledContent):

    file = silvaschema.Bytes(
        title=_(u"file"),
        description=_(u"File to upload as source data."),
        required=True)
    data_encoding = schema.Choice(
        title=_(u"character encoding"),
        description=_(u'Character encoding of the source data.'),
        source=encoding_source,
        required=False)


class CSVSourceAddForm(silvaforms.SMIAddForm):
    """CSVSource Add Form.
    """
    grok.context(ICSVSource)
    grok.name(u'Silva CSV Source')

    fields = silvaforms.Fields(ICSVSourceSchema)


class CSVSourceView(silvaviews.View):
    """View a CSVSource.
    """
    grok.context(ICSVSource)

    def render(self):
        return self.content.to_html(self.context, self.request)
