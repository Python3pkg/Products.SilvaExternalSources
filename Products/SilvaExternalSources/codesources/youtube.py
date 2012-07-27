# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Helpers for cs_youtube...

import urlparse

# XXX these should become the tests

# correct urls have a path which start with '/v/' and youtube netloc
# urls have which have a path that starts with '/watch' or with '/embed'
# need to get rebuild, invalid urls have a path different than that

# type one of url
#youtube_url = "http://www.youtube.com/watch?v=4T1BITS4Hz0&feature=g-all-u"

# type two of url
#youtube_url = "http://www.youtube.com/v/4T1BITS4Hz0"

# type three of url
#youtube_url = "http://www.youtube.com/embed/fwUHKgVc2zc"

# type four of url
#youtube_url = "http://www.youtube.com/v/4T1BITS4Hz0?version=3&amp;hl=nl_NL"

#type five of url
#youtube_url = "http://youtu.be/Lh6QPg5BGsE"

#type six of url invalid
#youtube_url = "http://youtube.be/v/Lh6QPg5BGsE"

#type seven of url invalid
#youtube_url = "http://youtube.com/embed?v=Lh6QPg5BGsE"

# print build_youtube_url(youtube_url)

# target url: http://www.youtube.com/v/4T1BITS4Hz0?version=3&amp;hl=nl_NL

def build_youtube_url(url):
    source_url = url

    parsed_url = urlparse.urlparse(source_url)

    # print "Parsed url: ", parsed_url

    # example ParseResult(scheme='http', netloc='www.youtube.com', path='/watch', params='', query='v=4T1BITS4Hz0&feature=g-all-u', fragment='')

    parsed_query = urlparse.parse_qs(parsed_url.query)

    # print "Parsed query: ", parsed_query

    # if structure to cover alle conditions based on path
    # the url is ok we have a netloc and a path

    if parsed_url.netloc.endswith('youtube.com') and parsed_url.path.startswith('/v/'):
        source_url = source_url
    elif parsed_url.netloc.endswith('youtube.com') and not 'v' in  parsed_query and parsed_url.path.startswith('/embed'):
        video_id = parsed_url.path.split('/')
        target_url = parsed_url.scheme, parsed_url.netloc, '/v/' + video_id [-1] , 0 ,0
        target_url = urlparse.urlunsplit(target_url)
        source_url = target_url
    elif parsed_url.netloc.endswith('youtube.com') and 'v' in  parsed_query and parsed_url.path.startswith('/watch'):
        target_url = parsed_url.scheme, parsed_url.netloc, '/v/' + parsed_query['v'][0], 0 ,0
        target_url = urlparse.urlunsplit(target_url)
        source_url = target_url
    elif parsed_url.netloc.endswith('youtu.be') and parsed_url.path.startswith('/'):
        target_url = parsed_url.scheme, 'youtube.com', '/v' + parsed_url.path, 0 ,0
        target_url = urlparse.urlunsplit(target_url)
        source_url = target_url
    else:
        source_url = None

    return source_url




