request = context.REQUEST
model = request.model

return model.to_html(request)
