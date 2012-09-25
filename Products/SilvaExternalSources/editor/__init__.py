# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core import conf as silvaconf

class CKEditorExtension(object):
    base = '++static++/Products.SilvaExternalSources.editor'
    plugins = {
        'silvaexternalsource': 'plugins/silvaexternalsource'
        }


class IEditorPluginResources(IDefaultBrowserLayer):
    silvaconf.resource('parameters.css')

extension = CKEditorExtension()
