# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Helpers for cs_youtube ...

import urllib.parse

from AccessControl import ModuleSecurityInfo

module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.codesources.youtube')


# correct urls have a path which start with '/v/' and youtube netloc
# urls have which have a path that starts with '/watch' or with '/embed'
# need to get formatted, invalid urls have a path different than that

module_security.declarePublic('validate_youtube_url')
def validate_youtube_url(value, REQUEST=None):
    """Validate that a url can be used as a youtube URL.

    >>> validate_youtube_url("http://www.youtube.com/watch?v=4T1BITS4Hz0&feature=g-all-u")
    True
    >>> validate_youtube_url("http://www.youtube.com/v/4T1BITS4Hz0")
    True
    >>> validate_youtube_url("http://youtube.com/v/4T1BITS4Hz0")
    True
    >>> validate_youtube_url("http://www.youtube.com/embed/fwUHKgVc2zc")
    True
    >>> validate_youtube_url("http://www.youtube.com/v/4T1BITS4Hz0?version=3&amp;hl=nl_NL")
    True
    >>> validate_youtube_url("http://youtu.be/Lh6QPg5BGsE")
    True
    >>> validate_youtube_url("http://youtube.be/v/Lh6QPg5BGsE")
    False
    >>> validate_youtube_url("http://youtube.com/embed?v=Lh6QPg5BGsE")
    False
    >>> validate_youtube_url("http://youtube.com/embed/videos/Lh6QPg5BGsE")
    False
    >>> validate_youtube_url("http://youtube.com/")
    False
    >>> validate_youtube_url("http://www.youtube.com/watch?foo=bar")
    False
    >>> validate_youtube_url("http://silvacms.org")
    False
    """
    return format_youtube_url(value) is not None


module_security.declarePublic('format_youtube_url')
def format_youtube_url(source_url):
    """Convert different format of youtube URLs to the one required by
    the flash player.

    >>> format_youtube_url("http://www.youtube.com/watch?v=4T1BITS4Hz0&feature=g-all-u")
    'http://www.youtube.com/v/4T1BITS4Hz0'
    >>> format_youtube_url("http://www.youtube.com/v/4T1BITS4Hz0")
    'http://www.youtube.com/v/4T1BITS4Hz0'
    >>> format_youtube_url("http://youtube.com/v/4T1BITS4Hz0")
    'http://www.youtube.com/v/4T1BITS4Hz0'
    >>> format_youtube_url("http://www.youtube.com/embed/fwUHKgVc2zc")
    'http://www.youtube.com/v/fwUHKgVc2zc'
    >>> format_youtube_url("http://www.youtube.com/v/4T1BITS4Hz0?version=3&amp;hl=nl_NL")
    'http://www.youtube.com/v/4T1BITS4Hz0'
    >>> format_youtube_url("http://youtu.be/Lh6QPg5BGsE")
    'http://www.youtube.com/v/Lh6QPg5BGsE'
    >>> format_youtube_url("http://youtube.be/v/Lh6QPg5BGsE")
    >>> format_youtube_url("http://youtube.com/embed?v=Lh6QPg5BGsE")
    >>> format_youtube_url("http://youtube.com/embed/videos/Lh6QPg5BGsE")
    >>> format_youtube_url("http://youtube.com/")
    >>> format_youtube_url("http://www.youtube.com/watch?foo=bar")
    """
    if source_url is None:
        return None

    parsed_url = urllib.parse.urlparse(source_url)
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    parsed_path = parsed_url.path.strip('/').split('/')

    if not len(parsed_path):
        return None

    def youtube_url(video_id):
        return urllib.parse.urlunsplit((
            parsed_url.scheme,
            'www.youtube.com',
            '/v/' + video_id,
            '',
            ''),)

    if parsed_url.netloc.endswith('youtube.com'):

        if parsed_path[0] == 'v' and len(parsed_path) == 2:
            return youtube_url(parsed_path[1])
        if parsed_path[0] == 'embed' and len(parsed_path) == 2:
            return youtube_url(parsed_path[1])

        if parsed_path[0] == 'watch':
            if 'v' in parsed_query:
                return youtube_url(parsed_query['v'][0])

    elif parsed_url.netloc.endswith('youtu.be'):

        if len(parsed_path) == 1:
            return youtube_url(parsed_path[0])

    return None




