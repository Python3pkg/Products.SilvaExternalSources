# Stupid utilities
def notEven((number, value)):
   if number % 2 == 0:
      return True
   return False

def notOdd((number, value)):
   if number % 2 != 0:
      return True
   return False

def onlyFirst((number, value)):
   return value

def clean(value):
   return value.replace(' ', '').replace('\n', '')

# Extract information
cleaned = map(clean, iframe.split('"'))
keys = map(onlyFirst, filter(notEven, enumerate(cleaned)))
values = map(onlyFirst, filter(notOdd,  enumerate(cleaned)))

# Check tags and structure
stdigest = ''.join(keys)
wanted_stdigest = '<iframewidth=height=frameborder=scrolling=marginheight=marginwidth=src=></iframe><br/><small><ahref=style=>ViewLargerMap</a></small>'
if stdigest != wanted_stdigest:
    return False

# Check that all urls link to maps.google.com
for key, value in zip(keys, values):
    if key.endswith('src=') or key.endswith('href='):
        if not value.startswith('http://maps.google.com/'):
            return False

return True
