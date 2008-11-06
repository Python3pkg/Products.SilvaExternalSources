## Script (Python) "public_or_preview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#return true if viewing public
#       false if viewing preview
if context.REQUEST['ACTUAL_URL'].split('/')[-1].find('preview') > -1:
    return False
return True
