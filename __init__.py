import install
import CodeSource, SQLSource, CSVSource, CodeSourceService
# Silva
from Products.Silva.ExtensionRegistry import extensionRegistry

has_makeContainerFilter = True
try:
    from Products.Silva.helpers import makeContainerFilter
except:
    has_makeContainerFilter = False

def initialize(context):
    if has_makeContainerFilter:
        context.registerClass(
            CodeSource.CodeSource,
            constructors = (
            CodeSource.addCodeSource,
            CodeSource.manage_addCodeSource
            ),
            icon = "www/codesource.png",
            container_filter = makeContainerFilter()
            )
        context.registerClass(
            SQLSource.SQLSource,
            constructors = (
            SQLSource.addSQLSource,
            SQLSource.manage_addSQLSource
            ),
            icon = "www/sqlsource.png",
            container_filter = makeContainerFilter()        
            )
    else:
        context.registerClass(
            CodeSource.CodeSource,
            constructors = (
            CodeSource.addCodeSource,
            CodeSource.manage_addCodeSource
            ),
            icon = "www/codesource.png"
            )
        context.registerClass(
            SQLSource.SQLSource,
            constructors = (
            SQLSource.addSQLSource,
            SQLSource.manage_addSQLSource
            ),
            icon = "www/sqlsource.png"
            )

    context.registerClass(
        CodeSourceService.CodeSourceService,
        constructors = (
        CodeSourceService.addCodeSourceService,
        CodeSourceService.manage_addCodeSourceService
        ),
        icon = "www/codesource.png"
        )

    from Products.SilvaExternalSources.silvaxml.xmlexport import initializeXMLExportRegistry
    initializeXMLExportRegistry()
