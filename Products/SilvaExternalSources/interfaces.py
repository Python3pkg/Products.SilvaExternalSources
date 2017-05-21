# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import Acquisition

from five import grok
from zope.interface import Interface, Attribute
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from silva.core.interfaces import ISilvaService, ISilvaLocalService
from silva.core.interfaces import IXMLZEXPExportable
from silva.core.interfaces import IVersionedNonPublishable, IVersion
from silva.core.interfaces import IAsset, IRoot


def availableSources(context):
    """List available sources in the site starting at context.
    """
    sources = {}
    while context is not None:
        for item in context.objectValues():
            if (IExternalSource.providedBy(item) and
                item.id not in sources and item.is_usable()):
                sources[item.id] = item
        if IRoot.providedBy(context):
            break
        context = Acquisition.aq_parent(context)
    sources = list(sources.items())
    sources.sort(key=lambda i: i[1].get_title().lower())
    return sources


@grok.provider(IContextSourceBinder)
def source_source(context):

    def make_term(identifier, source):
        return SimpleTerm(value=source,
                          token=identifier,
                          title=str(source.get_title()))

    return SimpleVocabulary([make_term(*t) for t in availableSources(context)])


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

    def get_icon():
        """Returns an icon associated to the code source. This would
        be a ZODB object.
        """

    def get_description():
        """Returns the purpose of this external source.

        The description is shown in the 'external data' element's editor.
        It can contain a description of the use of its parameters and the
        what data is will render in the document.
        """

    def is_previewable(**parameters):
        """Specify the previewability (in kupu) of the source
        """

    def is_cacheable(**parameters):
        """Returns the cacheability (true or false) for this source.

        Silva Document atempts to cache the public rendering. If a document
        references this external source, it will check for its cachability.
        If the data from this source can be cached this source will only be
        called once.
        """

    def is_usable():
        """Returns True if the source is usable in new contents.
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

    def set_usable(usable):
        """Set if the source is usable in new content.
        """


class ICodeSource(IEditableExternalSource, IXMLZEXPExportable):
    """Code source: an external source built in ZMI.
    """

    def get_data_encoding():
        """ Returns the encoding of source's data.

        Silva expects unicode for its document data. This parameter
        specifies the encoding of the original data so it can be properly
        converted to unicode when passing the data to the Silva Document.

        NOTE: This is usually only used *within* the code source
        implementation.
        """

    def test_source():
        """Test if the source is working or if it has problems. It
        should return None if there are no problems.
        """


class ISourceAssetVersion(IVersion):
    """A version of a source asset.
    """

    def get_controller(request):
        """Return the controller associated to the source.
        """

    def get_source():
        """Return the original source object associated to this asset,
        or raise a SourceError exception.
        """


class ISourceAsset(IVersionedNonPublishable, IExternalSource):
    """Source asset store a external source and parameters to render it
    """

    def get_viewable_source():
        """Return the original source object associated with the
        published version of the asset, or None if it is available or
        broken.
        """


class ISourceEditableVersion(IVersion):
    """A version of a content using the editor external source features
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
    identifier = Attribute("Source identifier")
    title = Attribute("User-friendly source title")
    script_id = Attribute("Script identifier used to render the source")
    description = Attribute("User-friendly source description")
    location = Attribute("Filesystem location, relative to the egg")

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


class IExternalSourceInstance(Interface):
    """Store parameters for a given source instance.
    """

    def get_source_identifier():
        """Return the source identifier corresponding to this
        source parameters.
        """

    def get_parameter_identifier():
        """Return an identfier that identifies uniquely those
        parameters.
        """

    def get_source_template():
        """Return a string used a template to warp around the result
        of the source.
        """

    def set_source_template(template):
        """Set a string to use as a template to warp around the result
        of the source.
        """


class IExternalSourceController(Interface):
    """This control an instance of a code source.

    This behave and follow the same API than a Silva form.
    """
    label = Attribute('Title of the code source instance')
    description = Attribute('Description of the code source instance')

    def new():
        """Create a new instance of the code source on the context
        object.
        """

    def copy(destination):
        """This copy the current instance of the code source into a
        another external source controller.
        """

    def create():
        """Create a new instance of the code source on the context
        object, and save the code source parameters from the current
        request into this new instance.
        """

    def save():
        """Save the code source parameters from the current request.
        """

    def remove():
        """This remove the current instance of the code source from
        the context object.
        """

    def render(view=False, preview=False):
        """Render the instance of the code source, with its parameters.

        ``preview`` if true will render the code source in preview
        mode (paying attention if the code source provides parameters
        in the request, and if it is previewable).

        ``view`` is an option for compatiblity with the content layout
        extension.
        """


class IExternalSourceManager(Interface):
    """Manage external source instances on an context object.
    """

    def new(source):
        """Create and return a new external source instance object to
        store a parameters for a new instance of this source on the
        context object.
        """

    def all():
        """Return all the identifiers of each parameter object
        available on the context object.
        """

    def remove(identifier):
        """Remove the parameter object associated with the given
        ``identifier`` from the context object.
        """

    def get_parameters(instance=None, name=None):
        """Return the parameters and the source associated to this
        instance or source.
        """

    def __call__(request, instance=None, name=None):
        """Retrieve the parameters and the source associated to this
        instance or source, and bind them into a controller together
        with a request.
        """


class ISourceErrors(Interface):

    def report(info):
        """Report an error.
        """

    def fetch():
        """Return a list of all reported errors.
        """

