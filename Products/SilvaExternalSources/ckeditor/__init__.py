# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

class CKEditorExtension(object):
    base = '++resource++Products.SilvaExternalSources.ckeditor'
    plugins = {
        'silvaexternalsource': 'plugins/silvaexternalsource'
        }

extension = CKEditorExtension()
