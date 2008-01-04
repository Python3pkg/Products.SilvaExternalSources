import install
import CodeSource, SQLSource, CSVSource
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

    #registerDirectory('views', globals())
    #registerTypeForMetadata(CSVSource.CSVSource.meta_type)

    from Products.SilvaExternalSources.silvaxml.xmlexport import initializeXMLExportRegistry
    initializeXMLExportRegistry()
