# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import install
import CodeSource, SQLSource, CSVSource, CodeSourceService
# Silva
from Products.Silva.ExtensionRegistry import extensionRegistry

from silva.core import conf as silvaconf

silvaconf.extensionName('SilvaExternalSources')
silvaconf.extensionTitle('Silva External Sources')
silvaconf.extensionDepends('SilvaDocument')

def initialize(context):
    from Products.SilvaExternalSources.silvaxml.xmlexport import initializeXMLExportRegistry
    initializeXMLExportRegistry()
