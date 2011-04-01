## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object_path, placement, model, version
##title=
##
pa = model.restrictedTraverse(object_path, None)
if not pa:
  return '<div class="warning">Embedded Page Asset not found: %s</div>'%(object_path)
viewable = pa.get_viewable()
if not viewable:
  return '<div class="warning">Embedded Page Asset not published: %s</div>'%(object_path)
return viewable.restrictedTraverse(['@@content.html'])()
