# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import ISilvaService, ISilvaLocalService, IAsset
from silva.core.interfaces import IXMLZEXPExportable
from silva.core.interfaces import IDataManager
from zope.interface import Interface, Attribute


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


class ICodeSource(IEditableExternalSource, IXMLZEXPExportable):
    """Code source: an external source built in ZMI.
    """

    def test_source():
        """Test if the source is working or if it has problems. It
        should return None if there are no problems.
        """


# Code source Service support.

class ICodeSourceService(ISilvaService, ISilvaLocalService):
    """Code source service.
    """

    def find_installed_sources():
        """Find all installed code sources. You can after call
        ``get_installed_sources`` to get the list of installed code
        sources.
        """

    def get_installed_sources():
        """Return all installed code sources.
        """

    def clear_installed_sources():
        """Clear the known list of installed code sources.
        """

    def get_installable_sources():
        """Return a list of all known installable code sources in this
        Silva site.
        """

    def get_installable_source(identifier=None, location=None):
        """Return a specific installable code source in this Silva
        site, defined either by its identifier or location, or return
        None if no installable code source matches.
        """


class ICodeSourceInstaller(Interface):
    """Install or update a specific code source.
    """
    identifier = Attribute(u"Source identifier")
    title = Attribute(u"User-friendly source title")
    script_id = Attribute(u"Script identifier used to render the source")
    description = Attribute(u"User-friendly source description")
    location = Attribute(u"Filesystem location, relative to the egg")

    def validate():
        """Return True if the source is correctly defined on the
        filesystem, that no required information is missing.
        """

    def is_installed(folder):
        """Return True if the source is installed in the given Silva
        container.
        """

    def install(folder):
        """Install in a specific Silva container an instance for this
        source, from the filesystem.
        """

    def update(source):
        """Update from the filesystem a specific source.
        """


class ICSVSource(IEditableExternalSource, IAsset):
    """An external source showing the content of a CSV file.
    """


# This define a parameter instance of a source.

class ISourceParameters(Interface):
    """Store parameters for a given source instance.
    """

    def __init__(source_identifier):
        """Create a new instance of the given source.
        """

    def get_source_identifier():
        """Return the source identifier corresponding to this
        source parameters.
        """


class IBoundSourceInstance(IDataManager):
    """Bind a request, context and source parameters together, to
    read, update and render a source.
    """
    identifier = Attribute(u"Source identifier")

    def get_source_and_form(request=None):
        """Return the associated source and form to the instance.
        """


class ISourceInstances(Interface):
    """Manage a set of source instances.
    """

    def new(source_identifier):
        """Return a new source instance identifier for the given
        source identifier.
        """

    def remove(instance_identifier, context, request):
        """Remove the identifier instance for the list of instances.
        """

    def bind(instance_identifier, context, request):
        """Bind the source to the given context and request.
        """

    # All the following methods let you access the instances like in
    # dictionnary.

    def items():
        pass

    def keys():
        pass

    def values():
        pass

    def get(instance_identifier):
        pass

    def __getitem__(instance_identifier):
        pass
