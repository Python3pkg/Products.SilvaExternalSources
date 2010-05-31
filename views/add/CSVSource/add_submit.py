from Products.Silva import mangle

# I18N stuff
from Products.Silva.i18n import translate as _


model = context.REQUEST.model
REQUEST = context.REQUEST

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    return model.edit['tab_edit']()

# validate form
from Products.Formulator.Errors import FormValidationError
try:
    result = context.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return context.add_form(message_type="error",
        message=context.render_form_errors(e))

# get id and set up the mangler
id = mangle.Id(model, result['object_id'])

# try to cope with absence of title in form (happens for ghost)
if result.has_key('object_title'):
    title = result['object_title']
else:
    title = ""

# if we don't have the right id, reject adding
id_check = id.validate()
if id_check == id.OK:
    id = str(id)
else:
    return context.add_form(message_type="error",
        message=context.get_id_status_text(id))

# get file, character encoding from the form
file = result.get('object_file')
character_set = result['object_character_set']
de = character_set.strip()

try:
    unicode('abcd', de, 'replace')
except LookupError:
    # unknown encoding, return error message
    m = _(
        'Unknown encoding ${enc}. CSVSource not added! ',
        mapping={'enc':de})
    return context.add_form(message_type="error", message=m)

try:
    model.manage_addProduct['SilvaExternalSources'].manage_addCSVSource(id, title, file)
except IOError, e:
    m = _(
        'Problem ${exception}',
        mapping={'exception':e})
    msg = unicode(m)
    return context.add_form(message_type="error", message=msg)
object = getattr(model, id)

# update last author info in new object
object.sec_update_last_author_info()

object.set_data_encoding(de)
# now go to tab_edit in case of add and edit, back to container if not.
if REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    m = _(
        'Added ${metatype} ${id}.',
        mapping={'metatype':object.meta_type, 'id':context.quotify(id)})
    return model.edit['tab_edit'](message_type="feedback", message=m)
