from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError

# I18N stuff
from Products.Silva.i18n import translate as _

###

model = context.REQUEST.model
view = context

try:
    result = view.rawdata_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg_type = 'feedback'

msg = u''

if result.has_key('csv_rawdata'):
    data = result['csv_rawdata']
    model.update_data(data)
    m = _('Raw data set. ')
    msg += unicode(m)

return view.tab_edit(message_type=msg_type, message=msg)
