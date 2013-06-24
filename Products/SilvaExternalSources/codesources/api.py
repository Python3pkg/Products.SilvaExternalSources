

from AccessControl import ModuleSecurityInfo
from AccessControl.security import checkPermission
from silva.app.document.interfaces import IDocument
from silva.core.interfaces import IAddableContents, IPublishable
from silva.core.interfaces import IAutoTOC
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


module_security.declarePublic('include_resource')
def include_resource(css=None, js=None, requires=[]):
    """Add a Javascript or CSS to the document head. It can depends on
    other resources, like for instance jquery::

      include_resource(js='http://url', requires=['jquery'])
    """
    pass


module_security.declarePublic('include_snippet')
def include_snippet(css=None, js=None, requires=[]):
    """Include a Javascript or CSS snippet in the document head. It
    can depends on other resources, like for instance jquery::

      include_resource(js='alert("I like JS !");', requires=['jquery'])
    """
    pass


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
