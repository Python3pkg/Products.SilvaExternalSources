from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

msg_type = 'feedback'

try:
    result = view.settings_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

model.sec_update_last_author_info()

if result.has_key('csv_description'):
    model.set_description(result['csv_description'])

if result.has_key('csv_headings'):
    model.set_headings(result['csv_headings'])

msg = ['Settings changed']

return view.tab_edit(message_type=msg_type, message=' '.join(msg))
