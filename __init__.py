import install
import CodeSource, SQLSource, CSVSource, CodeSourceService
# Silva
from Products.Silva.ExtensionRegistry import extensionRegistry

def initialize(context):
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
        icon = "www/codesource_service.png"
        )

    from Products.SilvaExternalSources.silvaxml.xmlexport import initializeXMLExportRegistry
    initializeXMLExportRegistry()
