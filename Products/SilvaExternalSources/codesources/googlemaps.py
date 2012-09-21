# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml.html
import re
# from urlparse import urlparse
from AccessControl import ModuleSecurityInfo

module_security = ModuleSecurityInfo('Products.SilvaExternalSources.codesources.googlemaps')


# Validate that iFrame code pasted into the codesource has a valid googlemaps
# URL and that there are no nested iFrames inside.
# iFrames may not have any inline styles.

# The URLs for googlemaps iframes must either have (www.)?google.(TLD) for the
# domain and /maps for the beginning of the path, or have maps.google(TLD).
# for the domain. They must begin with https? schemes if there is a scheme.

module_security.declarePublic('validate_googlemaps_iframe')
def validate_googlemaps_iframe(iframe, REQUEST=None):
    """Validate the googlemaps iFrame HTML and URLs.

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://www.google.com/"></iframe><br /><small><a href="http://www.google.com/" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    True

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://www.google.com/"></iframe>')
    True

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/skinnyelephants"></iframe><br /><small><a href="http://maps.google.com/skinnyelephantz" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    True

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?f=q&amp;ll=51.924216,4.481776&amp;output=embed"></iframe><br /><small><a href="https://maps.google.com/maps?f=q&amp;ll=51.924216,4.481776" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    True

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="maps.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782"></iframe><br /><small><a href="maps.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    True

    >>> validate_googlemaps_iframe('<IFRAME STYLE=ZOMG! WIDTH=425 HEIGHT=350 FRAMEBORDER=0 SCROLLING=no MARGINHEIGHT=0 MARGINWIDTH=0 SRC=www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782></IFRAME><BR><SMALL><A HREF="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" STYLE="COLOR:#00F;TEXT-ALIGN:LEFT">View Larger Map</a></SMALL>')
    False

    >>> validate_googlemaps_iframe('<IFRAME WIDTH=425 HEIGHT=350 FRAMEBORDER=0 SCROLLING=no MARGINHEIGHT=0 MARGINWIDTH=0 SRC=www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782></IFRAME><BR><SMALL><A HREF="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" STYLE=COLOR:#00F;TEXT-ALIGN:LEFT>View Larger Map</a></SMALL>')
    True

    >>> validate_googlemaps_iframe('<IFRAME WIDTH=425 HEIGHT=350 FRAMEBORDER=0 SCROLLING=no MARGINHEIGHT=0 MARGINWIDTH=0 SRC=www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782></IFRAME><BR><P><SMALL><A HREF="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" STYLE="COLOR:#00F;TEXT-ALIGN:LEFT">View Larger Map</a></SMALL>')
    True

    >>> validate_googlemaps_iframe('''<IFRAME WIDTH=425 HEIGHT=350 FRAMEBORDER=0 SCROLLING=no MARGINHEIGHT=0 MARGINWIDTH=0 SRC=www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782></IFRAME><BR><P><SMALL><A HREF="Javascript:'content'" STYLE="COLOR:#00F;TEXT-ALIGN:LEFT">View Larger Map</a></SMALL>''')
    False

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://infrae.com"></iframe><br /><small><a href="http://infrae.com" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    False

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.at/maps?f=q&amp;source=s_q&amp;hl=en&amp;geocode=&amp;q=Augasse+2-6,+Wien&amp;aq=0&amp;oq=augasse+2&amp;sll=47.696454,13.345766&amp;sspn=7.898759,22.115479&amp;t=h&amp;ie=UTF8&amp;hq=&amp;hnear=Augasse+2-6,+Alsergrund+1090+Wien&amp;z=14&amp;ll=48.231908,16.357079&amp;output=embed"></iframe><br /><small><a href="https://maps.google.at/maps?f=q&amp;source=embed&amp;hl=en&amp;geocode=&amp;q=Augasse+2-6,+Wien&amp;aq=0&amp;oq=augasse+2&amp;sll=47.696454,13.345766&amp;sspn=7.898759,22.115479&amp;t=h&amp;ie=UTF8&amp;hq=&amp;hnear=Augasse+2-6,+Alsergrund+1090+Wien&amp;z=14&amp;ll=48.231908,16.357079" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    True

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782"><iframe src="http://google.com.au/evilscript.pl"></iframe></iframe><br /><small><a href="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" style="color:#0000FF;text-align:left">View Larger Map</a></small>')
    False

    >>> validate_googlemaps_iframe('''<iframe script="javascript:alert('Playa')" width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782"><iframe src="http://google.com.au/evilscript.pl"></iframe></iframe><br /><small><a href="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" style="color:#0000FF;text-align:left">View Larger Map</a></small>''')
    False

    >>> validate_googlemaps_iframe('''<iframe style="color: red" width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782"><iframe src="http://google.com.au/evilscript.pl"></iframe></iframe><br /><small><a href="www.google.com/maps?saddr=Hotel+Ibis+Coimbra+%4040.205247,-8.426782" style="color:#0000FF;text-align:left">View Larger Map</a></small>''')
    False

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://www.google.com/"></iframe><iframe src="http://infrae.com"></iframe>')
    False

    >>> validate_googlemaps_iframe('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://www.google.com/"></iframe><form action="http://infrae.com"><a>Form</a></form>')
    False

    >>> validate_googlemaps_iframe('''<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.at/maps?f=q&amp;source=s_q&amp;hl=en&amp;geocode=&amp;q=Augasse+2-6,+Wien&amp;aq=0&amp;oq=augasse+2&amp;sll=47.696454,13.345766&amp;sspn=7.898759,22.115479&amp;t=h&amp;ie=UTF8&amp;hq=&amp;hnear=Augasse+2-6,+Alsergrund+1090+Wien&amp;z=14&amp;ll=48.231908,16.357079&amp;output=embed"></iframe><br /><small><a href="https://maps.google.at/maps?f=q&amp;source=s_q&amp;hl=en&amp;geocode=&amp;q=Augasse+2-6,+Wien&amp;aq=0&amp;oq=augasse+2&amp;sll=47.696454,13.345766&amp;sspn=7.898759,22.115479&amp;t=h&amp;ie=UTF8&amp;hq=&amp;hnear=Augasse+2-6,+Alsergrund+1090+Wien&amp;z=14&amp;ll=48.231908,16.357079&amp;output=embed" style="color:#0000FF;text-align:left">View Larger Map</a></small>''')
    True

    >>> validate_googlemaps_iframe('''<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://google.fa.ke/evil"></iframe><br /><small><a href="http://google.fa.ke/evil" style="color:#0000FF;text-align:left">View Larger Map</a></small>''')
    True
    """

    if iframe is None:
        return False

    tree = lxml.html.fragment_fromstring(iframe, create_parent=True)
    URLs = []
    elements = tree.findall('.//*')
    
    for element in elements:
        if element.tag == 'iframe':
            if (len(element.getchildren()) != 0 or
              'style' in element.keys() or
              'javascript' in element.values()):
                return False
        for key, value in element.items():
            #form actions, onclick, etc
            if (key.lower().startswith('on') or
              key.lower() == 'action' or 'javascript' in value.lower()):
                return False
            if key == 'src' or key == 'href':
               URLs.append(element.get(key))
 
        
    # still cannot check against google.fa.ke/eviladdress
    # Google lists http://www.google.com/supported_domains but it does change regularly
    _url_pattern = re.compile(r'^(https?://)?(www\.|maps\.)?google\.[a-z]{2,3}(\.[a-z]{2})?/(maps)?.*$')
    for value in URLs:
        if not _url_pattern.search(value):
          return False 
#        parsed = urlparse(value)
#
#        if parsed.scheme == '':
#          if not (parsed.path.endswith('google.com/maps') or 
#                  parsed.path.startswith('maps.google.')):
#              return False
#        elif parsed.scheme == 'http' or parsed.scheme == 'https':
#          # this will not catch google.com/someRandomThing 
#          # nor just google.com/
#          if not parsed.netloc.endswith('google.com'):
#              return False  
                    
    return True
