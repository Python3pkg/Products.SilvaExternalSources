## Script (Python) "ustr"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=s
##title=
##
if not same_type(s,''):
  s = str(s,'utf-8')
return s

