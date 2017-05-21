# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Acquisition import aq_get
from AccessControl.SecurityManagement import getSecurityManager


def _exec(self, bound_names, args, kw):
    """Call a Page Template"""
    if 'args' not in kw:
        kw['args'] = args
    bound_names['options'] = kw
    request = kw.get('REQUEST')
    if request is None:
        request = aq_get(self, 'REQUEST', None)
        if request is not None:
            response = request.response
            if 'content-type' not in response.headers:
                response.setHeader('content-type', self.content_type)
    else:
        del kw['REQUEST']
        bound_names['request'] = request

    security = getSecurityManager()
    bound_names['user'] = security.getUser()

    # Retrieve the value from the cache.
    keyset = None
    if self.ZCacheable_isCachingEnabled():
        # Prepare a cache key.
        keyset = {'here': self._getContext(),
                  'bound_names': bound_names}
        result = self.ZCacheable_get(keywords=keyset)
        if result is not None:
            # Got a cached value.
            return result

    # Execute the template in a new security context.
    security.addContext(self)

    try:
        result = self.pt_render(extra_context=bound_names)
        if keyset is not None:
            # Store the result in the cache.
            self.ZCacheable_set(result, keywords=keyset)
        return result
    finally:
        security.removeContext(self)
