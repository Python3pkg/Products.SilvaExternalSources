TODO:
=====

o Unit tests

o to_xml() implementation and use

o Check SQLSource for possible SQL injection bugs


SilvaExternalSources:
=====================

  The SilvaExternalSources extension adds the possibility to include data
  from non-Silva sources in Silva Documents. These non-Silva or external
  sources can for example be a relational database or the outcome of
  executing a Python script.

  Since an external source can potentially be resource intensive or a
  vunerability, only users with ZMI access (usualy site managers) can
  create external sources. It is their responsibilty to make sure no
  vunerabilities are exposed to the Authors.

  An external source object can expose - using a Formulator form - a set of
  parameters to the Author of a Silva Document. The use of these parameters
  as set by the Author is to be specified by the external source
  implementation.

  By implementing the IExternalSource interface, one can create new types
  of external sources. See 'interfaces.py' for more details on this.

  The SilvaExternalSources extension currently implements two external
  sources: 'Silva Code Source' and 'Silva SQL Source':

  Silva Code Source:

    This is replacement for the 'old' code_source.
    ...

  Silva SQL Source:

    This is a replacement for the 'old' SQLDataSource.
    ...
