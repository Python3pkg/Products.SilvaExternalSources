## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object_path, placement
##title=
##
pa = context.REQUEST.model.restrictedTraverse(object_path, None)
if not pa:
  return "<div>Embedded Page Asset not found: %s</div>"%(object_path)
viewable = pa.get_viewable()
if not viewable:
  return "<div>Embedded Page Asset not published: %s</div>"%(object_path)
view = viewable.restrictedTraverse(['@@publicview'])
return view.render_asset()
