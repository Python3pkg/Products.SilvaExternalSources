# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope import interface


class ISourceParameters(interface.Interface):
    """Store parameters for a given source instance.
    """

    def __init__(source_identifier):
        """Create a new instance of the given source.
        """

    def get_source_identifier():
        """Return the source identifier corresponding to this
        source parameters.
        """


class IBoundSourceInstance(interface.Interface):
    """Bind a request, context and source parameters together, to
    read, update and render a source.
    """
    identifier = interface.Attribute(u"Source identifier")

    def get_source_and_form(request=None):
        """Return the associated source and form to the instance.
        """

    def clear():
        """Erase all set parameters.
        """

    def update(parmeters):
        """Update stored parameters using the given HTTP query string.
        """

    def render():
        """Render the source.
        """


class ISourceInstances(interface.Interface):
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
