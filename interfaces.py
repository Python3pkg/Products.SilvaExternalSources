from Interface import Interface
from AccessControl import ModuleSecurityInfo

__allow_access_to_unprotected_subobjects__ = 1

module_security = ModuleSecurityInfo('Products.SilvaExternalSources.interfaces')

class IExternalSource(Interface):
    """ Access to an external source of data.
    """

    # ACCESSORS

    def form():
        """ Returns a Formulator form or None if not applicable.
        
        This Formulator form is used in the Silva Document 'external data'
        document element to render the parameters UI.
        """
        pass

    def to_html(REQUEST, **kw):
        """ Returns the HTML for inclusion in the rendered Silva HTML.
        """
        pass

    def to_xml(REQUEST, **kw):
        """ Returns XML for this source for inclusion in exported Silva XML.
        
        NOTE: The use of this feature is not yet fully defined!
        
        """
        pass

    def is_cacheable(**kw):
        """ Returns the cacheability (true or false) for this source.
        
        Silva Document atempts to cache the public rendering. If a document
        references this external source, it will check for its cachability.
        If the data from this source can be cached this source will only be
        called once.
        """
        pass

    def data_encoding():
        """ Returns the encoding of source's data.
        
        Silva expects unicode for its document data. This parameter
        specifies the encoding of the original data so it can be properly
        converted to unicode when passing the data to the Silva Document.
        
        NOTE: This is usually only used *within* the external source
        implementation.
        """
        pass

    def description():
        """ Returns the purpose of this external source.
        
        The description is shown in the 'external data' element's editor.
        It can contain a description of the use of its parameters and the
        what data is will render in the document.
        """
        pass

    def get_title(self):
        """Returns the title of this instance.
        """
        pass
