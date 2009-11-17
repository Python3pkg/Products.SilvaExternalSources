##parameters=show_title,document
request = context.REQUEST
view_method='view'

if show_title=='no':
  request.set('suppress_title','yes')

model = request['model']
html = getattr(model.restrictedTraverse(str(document), None), view_method)()

request.model = model
request.other['model'] = model

return html
