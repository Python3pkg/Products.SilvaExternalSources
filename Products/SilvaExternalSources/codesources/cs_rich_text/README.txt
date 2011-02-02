README for Code Source 'rich text'
=====================================

This README should reside inside a Silva Code Source called 'cs_rich_text',
designed to provide rich text editing using tinymce (via the tinymce formulator
field). 


Customizing encaptionate
------------------------
There is not much to customize.  This code source is rather a wrapper around
the rich text functionality provided by tinymce_field.  If you choose,
you can edit the 'render' pythonscript to add additional html tags around
the rendered rich text (e.g. a <div>, for styling / positioning purposes).


Parameters
----------
The only parameter is `rich text`, which is a tinymce field.  It is possible
to customize tinymce by editing the parameters of this field.

If you wish, you can add other fields to the parameters form and use them in your 
own variant, e.g. add an optional "class" parameter which adds a class to the
containing <div> tag suggested in the above section.

--
Improvements and variants are welcome.
aaltepet at infrae com