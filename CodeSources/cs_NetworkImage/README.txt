README for Network Image Code Source
====================================

This README should reside inside a Silva Code Source called 'network_image'.

This Code Source provides a means to insert an image outside of Silva into 
a document. A Silva Image only refers to images within Silva, and sometimes 
it's necessary to refer to an image on the Internet or internal network. For 
instance OSI, the Open Source Initiative, makes a logo available that 
indicates that software has a certified open source license. They 
specifically request that you *not* put the image on your own site, but link 
to the logo on their site. It's also possible to link to an image in Silva by
using the lookup window.

It includes parameters for image location, width, height, alt, alignment, 
link, and link tooltip.

This Code Source doesn't provide dynamic content so you can set the "Source 
is cacheable" option to on for efficient page rendering.


Customizing network_image
-------------------------
The code in the page template 'netimage' can be easily adjusted to your 
personal requirements. Change the css class for the hyperlink, etc. 


Parameters
----------
You can change fields in the parameters form, say, making the alt text
field required so there has to be an alt attribute.

If you wish, add other fields to the parameters form and use them in your 
own variant.

CSS selectors

The alignment parameter has values for the the standard Silva image 
alignments: default, align-left, align-center, align-right, float-left, 
and float-right. The align-center option wraps the image in a div, while
the others apply the class to the image.


--
Improvements and variants are welcome.
torvald at infrae com
