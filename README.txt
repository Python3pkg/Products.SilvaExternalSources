Copyright (c) 2002-2005 Infrae. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  SilvaExternalSources 0.10.3
  Author:     Jan-Wijbrand Kolman, Guido Goldstein
  Email:      jw at infrae.com, gst at infrae.com
  CVS:        $Revision: 1.14 $

SilvaExternalSources:

  The SilvaExternalSources extension adds the possibility to include
  data from non-Silva sources in Silva Documents. These non-Silva or
  external sources can for example be a relational database or the
  outcome of executing a Python script.

  Since an external source can potentially be resource intensive or a
  expose a vulnerability, only users with ZMI access (usualy site
  managers) can create external sources. It is their responsibilty to
  make sure no vunerabilities are exposed to the Authors.

  An external source object can expose - using a Formulator form - a set
  of parameters to the Author of a Silva Document. The actual use of
  these parameters (and the values set by the Author) is to be specified
  by the external source implementation.

  By implementing the IExternalSource interface, one can create new types
  of external sources. See 'interfaces.py' for more details on this.

  The SilvaExternalSources extension currently implements three
  external sources: 'Silva Code Source', 'Silva SQL Source' and
  'Silva CSV Source'.  The latter is special in that it also shows
  up as an asset in Silva. This is possible because no code is
  contained in a CSVSource.

  See also documentation in the doc subdirectory of this Product.

  KNOWN ISSUES:

    o For the CSVSource object the description field from the metadata
      system is used. In cases where this desciption field is not
      filled in, it might acquire its value from the source's
      container object.

    o Not all Formulator widgets can succesfully be used for
      parameters yet, in particular check boxes and multi selection
      fields. We are working on adding facilities to Formulator to
      improve this.

