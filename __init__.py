import install
import CodeSource, SQLSource
# Silva
from Products.Silva.ExtensionRegistry import extensionRegistry

def initialize(context):
    extensionRegistry.register(
        'SilvaExternalSources', 'Silva External Sources', context, [],
        install, depends_on='Silva')

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
