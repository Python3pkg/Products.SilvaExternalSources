from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.charset_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg_type = 'feedback'
msg = ''
de = result['csv_character_set'].strip()

try:
    unicode('abcd', de, 'replace')
except LookupError:
    # unknown encoding, return error message
    msg_type = 'error'
    msg = "Unknown encoding '%s'. Character encoding not saved! " % de
    return view.tab_edit(message_type=msg_type, message=msg)
else:
    model.set_data_encoding(de)
    msg += 'Encoding set to: %s ' % de

return view.tab_edit(message_type=msg_type, message=msg)
