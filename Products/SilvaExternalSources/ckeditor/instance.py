# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import uuid
import urllib
import logging

from five import grok
from silva.core.editor.interfaces import IText
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.ckeditor.interfaces import (
    ISourceInstances, IBindedSourceInstance, ISourceParameters)
from Products.SilvaExternalSources.ckeditor.utils import parse_qs
from Products.Formulator.interfaces import IBindedForm

logger = logging.getLogger('Products.SilvaExternalSources')


class SourceParameters(object):
    grok.implements(ISourceParameters)

    def __init__(self, source_identifier):
        self.__source_identifier = source_identifier

    def get_source_identifier(self):
        return self.__source_identifier


class BindedSourceInstance(object):
    grok.implements(IBindedSourceInstance)

    def __init__(self, parameters, context, request, manager):
        self.__parameters = parameters
        self.__identifier = parameters.get_source_identifier()
        self.__manager = manager
        self.context = context
        self.request = request

    @property
    def identifier(self):
        return self.__identifier

    def get_source_and_form(self, request=None):
        if request is None:
            request = self.request
        source = getattr(self.context, self.__identifier, None)
        if source is not None:
            if IExternalSource.providedBy(source):
                form = None
                formulator_form = source.get_parameters_form()
                if formulator_form is not None:
                    # If there is a formulator form, query its binding.
                    form = getMultiAdapter(
                        (formulator_form, request, self.context),
                        IBindedForm)
                    form.set_content(self.__parameters)
                return source, form
        return None, None

    def update_parameters(self, parameters):
        save_request = TestRequest(form=parse_qs(parameters))
        source, form = self.get_source_and_form(save_request)
        if source is None:
            raise ValueError("A source have been removed or renamed")
        if form is not None:
            form.save()
            # Mark the manager as changed to presist everything.
            self.__manager._p_changed = True

    def render(self):
        source, form = self.get_source_and_form()
        if source is None:
            return "<p>Source is missing</p>"
        values = {}
        if form is not None:
            values = form.read()
        try:
            html = source.to_html(self.context, self.request, **values)
        except:
            logger.exception('Error while rendering the external source')
            html = '<p>Error while rendering the external source</p>'
        return html


def proxy_method(method):
    name = method.__name__

    def inner(self, *args, **kw):
        return getattr(self._instances, name)(*args, **kw)

    inner.__name__ = name
    return inner


class SourceInstances(grok.Annotation):
    grok.context(IText)
    grok.implements(ISourceInstances)
    grok.provides(ISourceInstances)

    def __init__(self, *args):
        super(SourceInstances, self).__init__(*args)
        self._instances = {}

    def new(self, source_identifier):
        identifier = str(uuid.uuid1())
        self._instances[identifier] = SourceParameters(source_identifier)
        # Force ZODB changed (dict is not a PersistentDict)
        self._p_changed = True
        return identifier

    def remove(self, instance_identifier):
        del self._instances[instance_identifier]
        # Force ZODB changed (dict is not a PersistentDict)
        self._p_changed = True

    def bind(self, instance_identifier, context, request):
        return BindedSourceInstance(
            self[instance_identifier], context, request, self)

    @proxy_method
    def items(self):
        pass

    @proxy_method
    def keys(self):
        pass

    @proxy_method
    def values(self):
        pass

    @proxy_method
    def get(self, instance_identifier):
        pass

    @proxy_method
    def __getitem__(self, instance_identifier):
        pass


