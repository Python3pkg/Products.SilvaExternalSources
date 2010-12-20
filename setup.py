# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.3.3dev'

setup(name='Products.SilvaExternalSources',
      version=version,
      description="Externals sources for Silva Document",
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
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.services',
        'silva.core.upgrade',
        'silva.core.views',
        'silva.translations',
        'zeam.form.silva',
        'zeam.utils.batch',
        'zope.component',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.schema',
        ],
      )
