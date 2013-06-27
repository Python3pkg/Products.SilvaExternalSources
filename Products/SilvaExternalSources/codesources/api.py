

from AccessControl import ModuleSecurityInfo
from AccessControl.security import checkPermission
from silva.app.document.interfaces import IDocument
from silva.core.interfaces import IAddableContents, IPublishable
from silva.core.interfaces import IAutoTOC
from silva.fanstatic import Group, Snippet, ExternalResource
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest

module_security = ModuleSecurityInfo(
    'Products.SilvaExternalSources.codesources.api')


module_security.declarePublic('render_content')
def render_content(content, request, suppress_title=False):
    """Render a content for inclusion.
    """
    if not (checkPermission('zope2.View', content)
            or IBrowserRequest.providedBy(request)):
        # You can't see the content or don't have a valid request.
        return u''
    content = content.get_silva_object()
    if suppress_title:
        if IDocument.providedBy(content):
            version = content.get_viewable()
            if version is None:
                return u''
            details = getMultiAdapter((version, request), name="details")
            return details.get_text()
        if IAutoTOC.providedBy(content):
            toc = getMultiAdapter((content, request), name="toc")
            toc.update()
            return toc.render()
        return u''
    renderer = queryMultiAdapter((content, request), name='content.html')
    if renderer is not None:
        return renderer()
    return u''


def _include_resources(factory, resources, category, requires, bottom):

    def create(resource):
        return factory(resource, category=category,
                       depends=requires, bottom=bottom)

    if len(resources) == 1:
        result = create(resources[0])
    else:
        result = Group(map(create, resources))
    result.need()
    return result


module_security.declarePublic('include_resource')
def include_resource(css=None, js=None, requires=[], bottom=False):
    """Add a Javascript or CSS to the document head. It can depends on
    other resources, like for instance jquery::

      include_resource(js='http://url', requires=['jquery'])

    It returns a resource that can be used as dependencies again.
    """
    if css is None:
        if not isinstance(js, (list, tuple)):
            if js is None:
                raise ValueError("Resources to include are missing")
            resources = [js]
        else:
            resources = js
        category = 'js'
    else:
        if not isinstance(css, (list, tuple)):
            resources = [css]
        else:
            resources = css
        category = 'css'
    return _include_resources(
        ExternalResource, resources, category, requires, bottom)


module_security.declarePublic('include_snippet')
def include_snippet(css=None, js=None, requires=[], bottom=False):
    """Include a Javascript or CSS snippet in the document head. It
    can depends on other resources, like for instance jquery::

      include_resource(js='alert("I like JS !");', requires=['jquery'])

    It returns a resource that can be used as dependencies again.
    """
    if css is None:
        if js is None:
            raise ValueError("Snippet to include is missing")
        resources = [js]
        category = 'js'
    else:
        resources = css
        category = 'css'
    return _include_resources(
        Snippet, resources, category, requires, bottom)


module_security.declarePublic('get_publishable_content_types')
def get_publishable_content_types(context):
    """Return meta_types of content that can be published in the Silva
    site.
    """
    container = context.get_root()
    return IAddableContents(container).get_all_addables(require=IPublishable)


module_security.declarePublic('get_container_content_types')
def get_container_content_types(context):
    """Return meta_types of all content can be used in the Silva site.
    """
    container = context.get_root()
    return IAddableContents(container).get_all_addables()
