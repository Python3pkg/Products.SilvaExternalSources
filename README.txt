Copyright (c) 2002, 2003 Infrae. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  SilvaExternalSources 0.3
  Author:     Jan-Wijbrand Kolman
  Email:      jw at infrae.com
  CVS:        $Revision: 1.4 $

  TODO:

    o Make buttons for reset layout and reset parameters form in SQL Source

    o Unit tests

    o Define to_xml() implementation and use

    o Check SQLSource for possible SQL injection bugs

  SilvaExternalSources:

    The SilvaExternalSources extension adds the possibility to include data
    from non-Silva sources in Silva Documents. These non-Silva or external
    sources can for example be a relational database or the outcome of
    executing a Python script.

    Since an external source can potentially be resource intensive or a
    expose a vunerability, only users with ZMI access (usualy site
    managers) can create external sources. It is their responsibilty to
    make sure no vunerabilities are exposed to the Authors.

    An external source object can expose - using a Formulator form - a set
    of parameters to the Author of a Silva Document. The actual use of
    these parameters (and the values set by the Author) is to be specified
    by the external source implementation.

    By implementing the IExternalSource interface, one can create new types
    of external sources. See 'interfaces.py' for more details on this.

    The SilvaExternalSources extension currently implements two external
    sources: 'Silva Code Source' and 'Silva SQL Source':

    See also documentation in the doc subdirectory of this Product.
