from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError

# I18N stuff
from Products.Silva.i18n import translate as _

###

model = context.REQUEST.model
view = context

try:
    result = view.charset_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg_type = 'feedback'
msg = u''
de = result['csv_character_set'].strip()

try:
    unicode('abcd', de, 'replace')
except LookupError:
    # unknown encoding, return error message
    m = _('Unknown encoding ${enc}. Character encoding not saved! ')
    m.set_mapping({'enc':de})
    msg = unicode(m)
    msg_type = 'error'
    return view.tab_edit(message_type=msg_type, message=msg)
else:
    model.set_data_encoding(de)
    m = _('Encoding set to: ${enc} ')
    m.set_mapping({'enc':de})
    msg += unicode(m)

return view.tab_edit(message_type=msg_type, message=msg)
