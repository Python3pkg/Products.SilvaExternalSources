# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# prevent a circular import in Zope 2.12
import AccessControl

from Products.SilvaExternalSources import install
from Products.SilvaExternalSources.silvaxml.xmlexport import \
    initializeXMLExportRegistry

from silva.core import conf as silvaconf

silvaconf.extensionName('SilvaExternalSources')
silvaconf.extensionTitle('Silva External Sources')


def initialize(context):
    initializeXMLExportRegistry()
