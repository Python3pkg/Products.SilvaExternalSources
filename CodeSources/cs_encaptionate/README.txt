README for Code Source 'encaptionate'
=====================================

This README should reside inside a Silva Code Source called 'encaptionate',
designed to provide additional options when captioning images, especially
photos that need descriptions and credits. 


Customizing encaptionate
------------------------
The code in the page templete 'capsule' can be easily adjusted to your 
personal requirements. Change the header size for the title, etc. 

Note that the width of the div with class="encaptionator" is locally set
and determined by the width of the image. This keeps all the elements 
encapsulated vertically.


Parameters
----------
You can change fields in the parameters form, say, making the caption text
field required so there has to be a caption.

If you wish, add other fields to the parameters form and use them in your 
own variant, e.g. add an optional "More...." link that's appended to the 
caption text (you can use the credit for that now, but it appears on a
new line).


CSS style
---------
The selectors follow for reference. Presumably your styles will be 
in the site's frontend CSS. 

/* move into frontend stylesheet */
div.encaptionator {
  margin: 0.1em 0 0 0;
}
div.inset {
  padding : 0.6em 0.5em 0.5em 0.5em;
  border : 1px solid #85d600;
  background-color : #ebf797;
}
div.encaptionator h5 {
  margin : -0.3em 0 0.4em 0;
}
div.encaptionator p {
  font-size: 90%;
  margin: 0.4em 0 0 0;
  line-height: 1.2em;
}
div.encaptionator p.credit {
  margin-top: 0.3em;
}
div.encaptionator a:link {
  text-decoration: none;
}
div.encaptionator a:visited {
  text-decoration: none;
}
div.encaptionator a:hover {
  text-decoration: underline;
}
h3 + div.float-left {
  margin-top: 0.2em;
}

--
Improvements and variants are welcome.
kitblake at infrae com
