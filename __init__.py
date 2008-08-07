import install
import CodeSource, SQLSource, CSVSource, CodeSourceService
# Silva
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva import conf as silvaconf

silvaconf.extensionName('SilvaExternalSources')
silvaconf.extensionTitle('Silva External Sources')
silvaconf.extensionDepends('SilvaDocument')

def initialize(context):
    from Products.Silva.fssite import registerDirectory
    registerDirectory('views', globals())
    from Products.SilvaExternalSources.silvaxml.xmlexport import initializeXMLExportRegistry
    initializeXMLExportRegistry()
