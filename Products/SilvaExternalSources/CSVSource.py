# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
import csv
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
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Asset import Asset
from Products.Silva.Asset import AssetEditTab
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

# Asset must be used inherited before EditableExternalSource
class CSVSource(Folder, Asset, EditableExternalSource):
    """CSV Source is an asset that displays tabular data from a
    spreadsheet or database. The format of the uploaded text file
    should be &#8216;comma separated values&#8217;. The asset can
    be linked directly, or inserted in a document with the External
    Source element. If necessary, all aspects of the display can be
    customized in the rendering templates of the CSV Source.
    """
    grok.implements(ICSVSource)

    meta_type = "Silva CSV Source"
    security = ClassSecurityInfo()

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
        SilvaPermissions.AccessContentsInformation, 'get_file')
    def get_file(self):
        """Return the file content.
        """
        return self._raw_data

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_size')
    def get_file_size(self):
        """Get the size of the file as it will be downloaded.
        """
        if self._raw_data:
            return len(self._raw_data)
        return 0

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_mime_type')
    def get_mime_type(self):
        return 'text/csv'

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_filename')
    def get_filename(self):
        return self.getId() + '.csv'

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

    def _update_data(self, data):

        def convert_to_unicode(line):
            return map(
                lambda v: v.decode(self._data_encoding, 'replace'),
                line)

        try:
            csv_data = map(convert_to_unicode, csv.reader(StringIO(data)))
        except csv.Error as error:
            raise ValueError(u"Invalid CSV file: %s" % error.args[0])

        self._data = csv_data
        self._raw_data = data
        self.update_quota()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file')
    def set_file(self, file):
        return self._update_data(file.read())

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        self._data_encoding = encoding
        self._update_data(self._raw_data)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_table_class')
    def set_table_class(self, css_class):
        self._table_class = css_class

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_description')
    def set_description(self, desc):
        if not isinstance(desc, unicode):
            desc = desc.encode('utf-8')

        binding = getUtility(IMetadataService).getMetadata(self)
        binding.setValues('silva-extra', {'content_description' : desc})


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


class ICSVSourceFields(ITitledContent):

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

    fields = silvaforms.Fields(ICSVSourceFields)


class CSVSourceEditForm(silvaforms.SMISubForm):
    """CSVSource Edit Form.
    """
    grok.view(AssetEditTab)
    grok.order(10)

    label = _(u'Edit file content')
    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager

    fields = silvaforms.Fields(ICSVSourceFields).omit('id')
    fields['file'].fileSetLabel = _(
        u"Click the Upload button to replace the current CSV with a new one.")
    actions  = silvaforms.Actions(
        silvaforms.CancelEditAction(),
        silvaforms.EditAction())


class CSVSourceView(silvaviews.View):
    """View a CSVSource.
    """
    grok.context(ICSVSource)

    def render(self):
        return self.content.to_html(self.context, self.request)
