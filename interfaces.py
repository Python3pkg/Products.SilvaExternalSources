from Interface import Interface
from AccessControl import ModuleSecurityInfo

__allow_access_to_unprotected_subobjects__ = 1

module_security = ModuleSecurityInfo('Products.SilvaExternalSources.interfaces')

class IExternalSource(Interface):
    """Access to an external source of data.

    The ExternalSource is resposible for composing a Formulator form
    for the UI, to render the data in XHTML and XML and to specify
    its cacheability.
    """

    # ACCESSORS

    def form():
        """ Return the formulator form for the UI.
        """
        pass

    def to_html(REQUEST, **kw):
        """ Render the HTML for inclusion in the render Silva HTML.
        """
        pass

    def to_xml(REQUEST, **kw):
        """ Render the XML for this source.
        """
        pass

    def is_cacheable(REQUEST, **kw):
        """ Specify the cacheability.
        """
        pass
