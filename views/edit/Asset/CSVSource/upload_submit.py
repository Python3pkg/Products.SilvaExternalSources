from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg_type = 'feedback'
msg = ''

if result.has_key('file') and result['file'] is not None:
    fin = result['file']
    data = fin.read()
    if data:
        model.update_data(data)
        msg = 'Data uploaded. '


return view.tab_edit(message_type=msg_type, message=msg)
