README for Google Maps Code Source
==================================

This README should reside inside a Silva Code Source named 'cs_google_maps'.
The Code Source allows Authors to embed a Google Map in a document.

Customizing Google Maps Code Source
-----------------------------------

Currently the file google_maps_source is not being used. Instead,
the codesource expects the entire iframe code to be added by the user
rather than only a URL to the map.

The validation script, 'googlemaps.py', resides in the filesystem at
Products.SilvaExternalSources in 'codesources'. It validates both
the iframe code and the URLs inside.

Parameters
----------

The Google Maps codesource expects a string containing the entire iframe
HTML code that you get from Google Maps.

--
Improvements and variants are welcome.
