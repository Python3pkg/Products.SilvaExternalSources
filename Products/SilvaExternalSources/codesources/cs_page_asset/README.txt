README for Code Source 'Embed Page Asset'
=====================================

This README should reside inside a Silva Code Source called 'cs_page_asset'.
This code source provides internal content syndication of Silva Page Asset's in
the following two ways:
1) by using this code source to directly embed Silva Page Assets into a 
   Silva Page
2) by adding page assets as "sticky content" to a content layout within a 
   container. This pushes the rendered page asset onto every "Silva Page"
   using that content layout.  The Sticky Content Service uses this code source
   "behind the scenes" for storage and rendering purposes.

Customizing cs_page_asset
------------------------
There is not much to customize.  This code source is rather a wrapper around
the rendering view for Silva Page Asset versions..  If you choose,
you can edit the 'render' pythonscript to add additional html tags around
the rendered rich text (e.g. a <div>, for styling / positioning purposes).


Parameters
----------
This code source has two parameters:
1) `object_path` : the path to the Silva Page Asset
2) `placement` : used by the sticky content service to determine whether the
   page asset should be rendered "above" or "below" the unique page content.

If you wish, you can add other fields to the parameters form and use them in your 
own variant, e.g. add an optional "class" parameter which adds a class to the
containing <div> tag suggested in the above section.

--
Improvements and variants are welcome.
aaltepet at infrae com