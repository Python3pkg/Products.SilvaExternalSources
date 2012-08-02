# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from Products.Silva.testing import SilvaLayer
import Products.SilvaExternalSources
import transaction


class SilvaExternalSourcesLayer(SilvaLayer):
    default_products = SilvaLayer.default_products + [
        'SilvaExternalSources',
        'ZSQLiteDA'
        ]
    default_packages = SilvaLayer.default_packages + [
        'silva.app.document'
        ]

    def _install_application(self, app):
        super(SilvaExternalSourcesLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.app.document')
        app.root.service_extensions.install('SilvaExternalSources')
        transaction.commit()


FunctionalLayer = SilvaExternalSourcesLayer(Products.SilvaExternalSources)
