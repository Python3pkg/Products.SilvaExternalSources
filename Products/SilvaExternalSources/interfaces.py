# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import ISilvaService, IAsset
from zope.interface import Interface


class ICodeSourceService(ISilvaService):
    """Code source service.
    """


class IExternalSource(Interface):
    """ Access to an external source of data.
    """

    # ACCESSORS

    def get_parameters_form():
        """ Returns a Formulator form describing the paramters used by
        the external source or None if not applicable.

        This Formulator form is used in the Silva Document 'external data'
        document element to render the parameters UI.
        """

    def to_html(content, request, **parameters):
        """ Render the HTML for inclusion in the rendered Silva HTML.
        """


    def get_title():
        """Returns the title of this instance.
        """

    def get_description():
        """ Returns the purpose of this external source.

        The description is shown in the 'external data' element's editor.
        It can contain a description of the use of its parameters and the
        what data is will render in the document.
        """

    def is_previewable(**parameters):
        """ Specify the previewability (in kupu) of the source
        """

    def is_cacheable(**parameters):
        """ Returns the cacheability (true or false) for this source.

        Silva Document atempts to cache the public rendering. If a document
        references this external source, it will check for its cachability.
        If the data from this source can be cached this source will only be
        called once.
        """

    def get_data_encoding():
        """ Returns the encoding of source's data.

        Silva expects unicode for its document data. This parameter
        specifies the encoding of the original data so it can be properly
        converted to unicode when passing the data to the Silva Document.

        NOTE: This is usually only used *within* the external source
        implementation.
        """


class IEditableExternalSource(IExternalSource):
    """An external source where settings can be edited.
    """

    def set_description(description):
        """Set the description of the external source.
        """

    def set_data_encoding(encoding):
        """Set the output encoding of the external source.
        """

    def set_cacheable(cacheable):
        """Set cacheablility of the external source (boolean). If set
        to False, the output of the source should never be cached.
        """

    def set_previewable(previewable):
        """Set previewablility of the external source in the WYSIWYG (boolean).
        """


class ICodeSource(IEditableExternalSource):
    """Code source: an external source built in ZMI.
    """


class ICSVSource(IEditableExternalSource, IAsset):
    """An external source showing the content of a CSV file.
    """
