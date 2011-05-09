# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaExternalSources import install

from silva.core import conf as silvaconf

silvaconf.extension_name('SilvaExternalSources')
silvaconf.extension_title('Silva External Sources')
silvaconf.extension_default()
