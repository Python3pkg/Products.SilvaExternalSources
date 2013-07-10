
from AccessControl import ModuleSecurityInfo
from AccessControl.security import checkPermission
from silva.app.document.interfaces import IDocument
from silva.core.interfaces import IAddableContents, IPublishable, ITreeContents
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
        # suppress title is not supported for other contents, render them publicly.
    renderer = queryMultiAdapter((content, request), name='content.html')
    if renderer is not None:
        return renderer()
    return u''


def _include_resources(factory, resources, category, requires, bottom):

    def create(resource, depends):
        return [factory(resource, category=category,
                        depends=depends, bottom=bottom)]

    # If the ordering in fanstatic would not randomize the relative
    # order of the resources the code would be:
    # if len(resources) == 1:
    #     result = create(resources[0], requires)
    # else:
    #     result = Group(map(lambda r: create(r, requires), resources))

    # But instead we have to make each resource depend on each other.
    for resource in resources:
        requires = create(resource, requires)
    result = requires[0]

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
        resources = [css]
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


module_security.declarePublic('get_content_tree')
def get_content_tree(context, depth):
    # This is extremely slow and performance-wise bad
    return ITreeContents(context).get_tree(depth)


module_security.declarePublic('get_content_public_tree')
def get_content_public_tree(context, depth):
    # This is extremely slow and performance-wise bad
    return ITreeContents(context).get_public_tree(depth)



