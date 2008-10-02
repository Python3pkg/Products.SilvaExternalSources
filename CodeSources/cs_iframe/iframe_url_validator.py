##parameters=value, request

for url in context.allowed_urls:
    if value.startswith(url):
        return True
