====================
SilvaExternalSources
====================

The SilvaExternalSources extension for `Silva`_ that gives you the
possibility to include data from non-Silva sources inside Silva
documents and Silva pages. These non-Silva or external sources can for
example be a relational database or the outcome of executing a Python
script.

Since an external source can potentially be resource intensive or a
expose a vulnerability, only users with ZMI access (usualy site
managers) can create external sources. It is their responsibilty to
make sure no vunerabilities are exposed to the Authors.

An external source object can expose - using a Formulator form - a set
of parameters to the Author of a Silva Document. The actual use of
these parameters (and the values set by the Author) is to be specified
by the external source implementation.

By implementing the IExternalSource interface, one can create new types
of external sources. See ``interfaces.py`` for more details on this.

The SilvaExternalSources extension currently implements three
external sources: *Silva Code Source*, *Silva SQL Source* and
*Silva CSV Source*.  The latter is special in that it also shows
up as an asset in Silva. This is possible because no code is
contained in a CSVSource.

Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/Products.SilvaExternalSources

.. _Silva: http://silvacms.org
