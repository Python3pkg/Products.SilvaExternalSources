# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# prevent a circular import in Zope 2.12
import AccessControl

from Products.SilvaExternalSources import install

from silva.core import conf as silvaconf
silvaconf.extensionName('SilvaExternalSources')
silvaconf.extensionTitle('Silva External Sources')

