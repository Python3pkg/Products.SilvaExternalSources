from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

model.sec_update_last_author_info()

if result.has_key('csv_title'):
    title = result['csv_title'].strip()
    model.set_title(title)

if result.has_key('csv_description'):
    desc = result['csv_description'].strip()
    model.set_description(desc)

msg = ['Title and Description changed.']
msg_type = 'feedback'

return view.tab_edit(message_type=msg_type, message=' '.join(msg))
