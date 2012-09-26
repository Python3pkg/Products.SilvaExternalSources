##parameters=value, REQUEST

if not value:
    return False

value = value.strip()

for possible_urls in context.allowed_urls:
    for url in possible_urls.split():
        if value.startswith(url):
            return True

return False
