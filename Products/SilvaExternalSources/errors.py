
from AccessControl.security import checkPermission

from five import grok
from zope.i18n import translate
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IPreviewLayer
from silva.translations import translate as _


class SourceError(ValueError):
    """Error related with the handling of source objects.
    """

    def message(self):
        return _(u"External Source errored during the processing.")



class SourceErrorView(silvaviews.Render):
    grok.context(SourceError)

    def render(self):
        if IPreviewLayer.providedBy(self.request):
            return translate(self.context.message(), context=self.request)
        return u""


class SourceRenderingError(SourceError):

    def __init__(self, manager, info):
        super(SourceRenderingError, self).__init__(manager, info)
        self.identifier = manager.getSourceId()
        self.manager = manager
        self.info = info


class SourceRenderingErrorView(silvaviews.Render):
    grok.context(SourceRenderingError)

    def update(self):
        self.preview = IPreviewLayer.providedBy(self.request)
        self.title = self.context.manager.label
        self.info = self.context.info
        self.manage = checkPermission(
            'silva.ManageSilvaSettings', self.context.manager.context)


class SourcePreviewError(SourceError):

    def __init__(self, manager):
        super(SourcePreviewError, self).__init__(manager)
        self.identifier = manager.getSourceId()
        self.manager = manager


class SourcePreviewErrorView(silvaviews.Render):
    grok.context(SourcePreviewError)

    def update(self):
        self.title = self.context.manager.label
        self.editable = self.context.manager.editable()
        self.widgets = self.context.manager.fieldWidgets(display=True)


class SourceMissingError(SourceError):
    """The source is not available.
    """

    def __init__(self, identifier):
        super(SourceMissingError, self).__init__(identifier)
        self.identifier = identifier

    def message(self):
        return _(u"External Source ${identifier} is not available.",
                 mapping=dict(identifier=self.identifier))


class ParametersError(SourceError):
    """The parameters are broken.
    """

    def message(self):
        return _("Error while validating the External Source parameters.")


class ParametersMissingError(ParametersError):
    """The parameters are missing.
    """

    def message(self):
        return _("External Source parameters are missing.")


