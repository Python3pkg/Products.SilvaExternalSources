from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

if result.has_key('file'):
    data = result['file'].read()
    model.update_data(data)

msg = ['Data uploaded and changed']
msg_type = 'feedback'

return view.tab_edit(message_type=msg_type, message=' '.join(msg))
