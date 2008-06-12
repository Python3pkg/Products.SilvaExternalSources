README for Code Source 'related_info'
=====================================

This README should reside inside a Silva Code Source named 'related_info'.
The Code Source is designed to allow Authors to locate a capsule of related
information within the document flow, and format it as a portlet for sidebar
content. The layout is fully controlled by css.

Customizing Related Info
------------------------
The code in the page template named 'capsule' can be easily adjusted to your
personal requirements. Change the header size for the title, etc.

Parameters
----------
You can adjust the fields in the parameters form. Make the heading required,
add a field for a link tooltip, etc.

CSS style
---------
The selectors follow for reference. The alignment div is a positioning
wrapper that insures flowing text wraps with some air, e.g.:

.float-left {
  float: left;
  margin: 0.3em 0.9em 0.5em 0em;
}

If the align-left alignment is chosen the div is skipped, as that's the 
default placement.  

For the inner div there are default css class names in the page template,
and if the Author doesn't enter a class, the default will be rendered. 

The classes are "info plot clover":
+ 'info' defines the width and determines the typography. If you want the
  capsule to be pure text, without being boxed in like a portlet, enter
  just 'info' into the class field (this overrides the default).
+ The 'plot' selector formats the capsule as a portlet. It plots the margin
  and the padding to the border. For centered display there is some logic
  in the template that add a local style setting the right and left
  margins to auto. This overrides the inherited right/left margin in the 
  plot selector in the stylesheet and ensures it will be centered.
+ The 'clover' class defines colors, setting the background and border of 
  the portlet, and is meant to be variable.

The style field can also be used to shift the vertical position of the
capsule, e.g. "margin-top:0.3em".

div.info {
  width: 184px;
  text-align: left; /* in case of centered wrapper */
}
div.info h2 {
  margin: 0 0 0.3em;
  font-size: 1.6em;
  color: #436;
  background-color: transparent;
}
div.info p {
  line-height: 130%;
}

div.plot {
  margin-top: 1.1em;
  margin-bottom: 0.7em;
  padding: 0.5em 0.7em 0.2em;
}

div.clover {
  border: 1px solid #83a99e;
  background-color: #c0eae7;
  background-image: url("<dtml-var root>/images/backgrounds/bgClover.gif");
  background-repeat: repeat-x;
}


--
Improvements and variants are welcome.
kitblake at infrae com
