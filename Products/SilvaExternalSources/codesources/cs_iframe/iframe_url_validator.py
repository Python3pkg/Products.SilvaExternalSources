## Script (Python) "iframe_url_validator"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=value, REQUEST
##title=
##
if not value:
    return False

value = value.strip()

for possible_urls in context.allowed_urls:
    for url in possible_urls.split():
        if value.startswith(url):
            return True

return False
