from Products.Formulator.Errors import FormValidationError

# I18N stuff
from Products.Silva.i18n import translate as _

###

model = context.REQUEST.model

try:
    result = context.charset_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error", message=context.render_form_errors(e))

msg_type = 'feedback'
msg = u''
de = result['csv_character_set'].strip()

try:
    unicode('abcd', de, 'replace')
except LookupError:
    # unknown encoding, return error message
    m = _(
        'Unknown encoding ${enc}. Character encoding not saved! ',
        mapping={'enc':de})
    msg_type = 'error'
    return context.tab_edit(message_type=msg_type, message=m)
else:
    model.set_data_encoding(de)
    m = _(
        'Encoding set to: ${enc} ',
        _mapping={'enc':de})
    msg += m

return context.tab_edit(message_type=msg_type, message=msg)
