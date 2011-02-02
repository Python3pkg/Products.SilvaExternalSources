## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=rich_text
##title=
##
return context.parameters.rich_text.render_view(rich_text)