
import urllib

from five import grok
from zope import schema
from zope.interface import Interface

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Acquisition import aq_base
from OFS import SimpleItem

from Products.Silva.Publishable import NonPublishable
from Products.Silva.SilvaObject import ViewableObject
from Products.Silva import SilvaPermissions as permissions
from Products.SilvaExternalSources.interfaces import IExternalSourceManager
from Products.SilvaExternalSources.interfaces import SourceError
from Products.SilvaExternalSources.interfaces import ISourceAsset, source_source

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.translations import translate as _
from silva.ui.rest import RedirectToPage
from silva.core.views import views as silvaviews

from zeam.form import silva as silvaforms
from zeam.component import getWrapper


class SourceAsset(NonPublishable, ViewableObject, SimpleItem.SimpleItem):
    """A source asset stores a external source and a set of its parameters.x
    """
    meta_type = "Silva Source Asset"
    grok.implements(ISourceAsset)
    silvaconf.icon('www/codesource.png')
    security = ClassSecurityInfo()

    _parameter_identifier = None

    security.declarePrivate('set_parameter_identifier')
    def set_parameters_identifier(self, identifier):
        self._parameter_identifier = identifier
        if hasattr(aq_base(self), '_v_original_source'):
            delattr(self, '_v_original_source')

    security.declarePrivate('get_controller')
    def get_controller(self, request):
        factory = getWrapper(self, IExternalSourceManager)
        return factory(request, instance=self._parameter_identifier)

    security.declarePrivate('get_original_source')
    def get_original_source(self):
        if not hasattr(aq_base(self), '_v_original_source'):
            manager = getWrapper(self, IExternalSourceManager)
            _, source = manager.get_parameters(self._parameter_identifier)
            self._v_original_source = source
        return self._v_original_source

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_parameters_form')
    def get_parameters_form(self):
        return None

    security.declareProtected(
        permissions.AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        return self.get_controller(request).render()

    def get_description(self):
        try:
            source = self.get_original_source()
            return source.get_description()
        except SourceError:
            return _('Broken or missing source.')

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_icon')
    def get_icon(self):
        try:
            source = self.get_original_source()
            return source.get_icon()
        except SourceError:
            return None

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_usable')
    def is_usable(self):
        return True

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_previewable')
    def is_previewable(self):
        try:
            source = self.get_original_source()
            return source.is_previewable()
        except SourceError:
            return False

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_cacheable')
    def is_cacheable(self):
        try:
            source = self.get_original_source()
            return source.is_cacheable()
        except SourceError:
            return False


InitializeClass(SourceAsset)


class ISourceSelectField(Interface):
    source = schema.Choice(
        title=_(u"Select an external source"),
        source=source_source,
        required=True)


class SourceAssetAddForm(silvaforms.SMIAddForm):
    """Add form for a link.
    """
    grok.context(ISourceAsset)
    grok.name(u'Silva Source Asset')

    fields = silvaforms.Fields(ISourceSelectField)
    titleFields = silvaforms.Fields(ITitledContent)
    actions = silvaforms.Actions(silvaforms.CancelAddAction())
    source = None

    def publishTraverse(self, request, name):
        factory = getWrapper(self.context, IExternalSourceManager)
        try:
            self.source = factory(request, name=urllib.unquote(name))
        except SourceError:
            parent = super(SourceAssetAddForm, self)
            return parent.publishTraverse(request, name)
        self.fields = self.titleFields
        self.__name__ = '/'.join((self.__name__, name))
        return self

    def updateWidgets(self):
        super(SourceAssetAddForm, self).updateWidgets()
        if self.source is not None:
            self.fieldWidgets.extend(self.source.widgets())

    @silvaforms.action(
        _(u"Select source"),
        available=lambda form: form.source is None,
        implements=silvaforms.IDefaultAction,
        accesskey=u'ctrl+s')
    def select_source(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        raise RedirectToPage(sub_tab=data['source'].getId())

    @silvaforms.action(
        _(u"Save"),
        available=lambda form: form.source is not None,
        implements=silvaforms.IDefaultAction,
        accesskey=u'ctrl+s')
    def save(self):
        data, errors = self.extractData()
        source_data, source_errors = self.source.extractData()
        if errors or source_errors:
            return silvaforms.FAILURE
        try:
            content = self._add(self.context, data)
        except ValueError, error:
            self.send_message(error.args[0], type=u"error")
            return silvaforms.FAILURE
        factory = getWrapper(content, IExternalSourceManager)
        source = factory(self.request, name=self.source.getSourceId())
        source.create()
        content.set_parameters_identifier(source.getId())
        raise RedirectToPage(content=content)


class SourceAssetEditForm(silvaforms.SMIEditForm):
    grok.context(ISourceAsset)

    actions = silvaforms.Actions(silvaforms.CancelEditAction())

    def __init__(self, context, request):
        super(SourceAssetEditForm, self).__init__(context, request)
        self.controller = context.get_controller(request)

    def updateWidgets(self):
        super(SourceAssetEditForm, self).updateWidgets()
        if self.controller is not None:
            self.fieldWidgets.extend(self.controller.widgets())

    @silvaforms.action(
        _(u"Save"),
        implements=silvaforms.IDefaultAction,
        accesskey=u'ctrl+s')
    def save(self):
        return self.controller.save()


class SourceAssetView(silvaviews.View):
    grok.context(ISourceAsset)

    def update(self):
        self.msg = None
        self.controller = None
        try:
            self.controller = self.content.get_controller(self.request)
        except SourceError, error:
            self.msg = error.to_html()

    def render(self):
        if self.msg:
            return self.msg
        return self.controller.render()
