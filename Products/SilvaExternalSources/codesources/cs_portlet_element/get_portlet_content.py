##parameters=show_title,document
request = context.REQUEST
view_method='view'

if show_title=='no':
  request.set('suppress_title','yes')

return getattr(context.restrictedTraverse(str(document), None), view_method)()
