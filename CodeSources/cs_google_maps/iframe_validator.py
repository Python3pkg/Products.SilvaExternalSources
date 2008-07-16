##parameters=iframe, request

# Utilities I don't like
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

def removeXmlData(value):
   xml = False
   cleaned = ''
   for letter in value:
      if letter == '<':
         xml = True
      elif letter == '>':
         xml = False
      elif not xml:
         continue
      cleaned += letter

   return cleaned

# Extract information
cleaned = map(clean, iframe.split('"'))
keys = map(onlyFirst, filter(notEven, enumerate(cleaned)))
values = map(onlyFirst, filter(notOdd,  enumerate(cleaned)))

# Check tags and structure
stdigest = removeXmlData(''.join(keys))
wanted_stdigest = '<iframewidth=height=frameborder=scrolling=marginheight=marginwidth=src=></iframe><br/><small><ahref=style=></a></small>'
if stdigest != wanted_stdigest:
    return False

# Check that all urls link to maps.google.com
for key, value in zip(keys, values):
    if key.endswith('src=') or key.endswith('href='):
        if not (value.startswith('http://maps.google.') or value.startswith('http://www.google.')):
            return False

return True
