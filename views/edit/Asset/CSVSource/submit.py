from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError

# I18N stuff
from Products.Silva.i18n import translate as _

###

model = context.REQUEST.model

try:
    result = context.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error", message=context.render_form_errors(e))

model.sec_update_last_author_info()

if result.has_key('csv_title'):
    title = result['csv_title'].strip()
    model.set_title(title)

if result.has_key('csv_description'):
    desc = result['csv_description'].strip()
    model.set_description(desc)

m = _('Title and Description changed.')

msg_type = 'feedback'

return context.tab_edit(message_type=msg_type, message=m)
