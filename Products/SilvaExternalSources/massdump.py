
from AccessControl import ModuleSecurityInfo, getSecurityManager
from zExceptions import Unauthorized
import pkg_resources
import os

from .CodeSourceService import CodeSourceInstallable


module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.massdump')

module_security.declarePublic('massdump')
def massdump(container, extension_name):
    user = getSecurityManager().getUser()
    if not user.has_role('Manager'):
        raise Unauthorized()
    exported = []
    extension = pkg_resources.working_set.by_key.get(extension_name)
    if extension is None:
        raise ValueError('Unknown extension', extension_name)
    directory = os.path.dirname(extension.load_entry_point(
            'Products.SilvaExternalSources.sources', 'defaults').__file__)
    for source in container.objectValues('Silva Code Source'):
        identifier = source.getId()
        target = os.path.join(directory, identifier)
        location = (
            extension.project_name + ':' +
            target[len(extension.location):])

        if source.get_fs_location() not in (None, location):
            continue
        if not os.path.exists(target):
            os.makedirs(target)
        source._fs_location = location
        installable = CodeSourceInstallable(location, target, [])
        installable.export(source)
        exported.append(location)
    return exported
