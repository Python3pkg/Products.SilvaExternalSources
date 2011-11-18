# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '3.0dev'

tests_require = [
    'silva.app.document [test]',
    'Products.Silva [test]',
    ]

# Products.ZSQLMethods should be as an option ?

setup(name='Products.SilvaExternalSources',
      version=version,
      description="Externals content sources to embed in rich text in Silva.",
      long_description=open(os.path.join("Products", "SilvaExternalSources", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaExternalSources", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='silva cms document external sources',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/download/SilvaExternalSources',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Formulator',
        'Products.Silva',
        'Products.SilvaMetadata',
        'Products.ZSQLMethods',
        'five.grok',
        'lxml',
        'megrok.chameleon',
        'setuptools',
        'silva.core.conf',
        'silva.core.editor',
        'silva.core.editor',
        'silva.core.interfaces',
        'silva.core.services',
        'silva.core.views',
        'silva.translations',
        'silva.ui',
        'zeam.form.silva',
        'zeam.utils.batch',
        'zope.component',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        ],
      entry_points="""
      [zodbupdate]
      renames = Products.SilvaExternalSources:CLASS_CHANGES
      [Products.SilvaExternalSources.sources]
      defaults = Products.SilvaExternalSources.codesources
      [silva.core.editor.extension]
      source = Products.SilvaExternalSources.editor:extension
      [silva.ui.resources]
      source = Products.SilvaExternalSources.editor:IEditorPluginResources
      """,
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
