README for MultiTOC Code Source
===============================

This README should reside inside a Silva Code Source named 'cs_multitoc'. The
Code Source allows Authors to place a listing of the contents of a container
that's located elsewhere in the site. Multiple containers can be listed, one
after the other. Authors can choose which Silva content types to list, such
as documents, folders, or files.

The listing can be inserted in the document flow like a normal TOC, or
encapsulated as a portlet for sidebar content. The rendering matches Silva
typographical selectors, and layout is fully controlled by css.

Since this Code Source provides dynamic content, you should not turn on the
"Source is cacheable" option.


Silva Content Types
-------------------
Authors can configure what sort of content types to list. These should be 
separated with a comma in the "content types to list" field like so: 
Silva Document, Silva Folder, Silva Image, Silva File
If you want to list another content type you can always hover over its icon 
to see its name in the tooltip.

Customizing MultiTOC
--------------------
The code in the page template named 'multi_toc' can be easily adjusted to
your personal requirements. Change the header size for the title, etc.

Parameters
----------
You can adjust the fields in the parameters form. Make the heading required,
add a field for a link tooltip, etc.

CSS style
---------
The alignment div is a positioning wrapper that also ensures flowing text
wraps with some air, e.g.:

.float-left {
  float: left;
  margin: 0.3em 0.9em 0.5em 0em;
}

If the align-left alignment is chosen the div is skipped, as that's the
default placement. This can be changed by adding a value to the parameter
field.

For the inner div an Author can add css class names that format a portlet. 

The style field can be used to shift the vertical position of the capsule,
e.g. "margin-top:0.3em".

If the display headings is turned on, the first container heading gets a
class="interheading" attribute, in case the vertical spacing between it 
and the capsule heading, or surrounding div, needs to be adjusted.

Error handling
--------------
There is a tal:on-error in the loop so that authors who somehow typo the 
path don't get an "External source is broken" message when (pre)viewing 
the rendered document. Thanks to Irene Fellner at WU Wien for the tip. 

You can edit the error message on line 22 of multi_toc. You can also have
it fail silently by making the errormessage nothing. Note that if you
change other code and cause an error the message will remain the same,
even though the path may be valid.

--
Improvements and variants are welcome.
Hard work by eric at infrae com, layout by kitblake at infrae com