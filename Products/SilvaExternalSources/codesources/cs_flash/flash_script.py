##parameters=REQUEST, model, version, ref, width, height, play='true', quality='high', params=''

asset_url = ref.absolute_url()
if width == '':
    width_attr = ''
else:
    width_attr = 'width="%s" ' % width

if height == '':
    height_attr = ''
else:
    height_attr = 'height="%s" ' % height

param_tags = ''
param_attrs = ''
if params != '':
    start = 0
    param_list = []
    while start < len(params):
        i = params.find('=', start)
        if i > -1:
            name = params[start:i].strip()
        else:
            break
        i = params.find('"', i) + 1
        j = params.find('"', i)
        if i > -1 and j > -1:
            value = params[i:j].strip()
        else:
            break
        param_list.append((name, value))
        start = j + 1
    for name, value in param_list:
        param_tags = param_tags + '\n  <param name="' + name \
                + '" value="' + value + '" />'
        param_attrs = param_attrs + '\n    ' + name + '="' + value + '" '

# the loop parameter is not here anymore, it was not working with some animations.

return """
<p class="p">
<object %s%s
  classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
  codebase="http://active.macromedia.com/flash5/cabs/swflash.cab#version=5,0,0,0">
  <param name="movie" value="%s" />
  <param name="play" value="%s" />
  <param name="quality" value="%s" />%s
  <comment>
  <embed %s%ssrc="%s" play="%s" quality="%s"
    pluginspage="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash"
    swLiveConnect="true"%s />
  </comment>
</object>
</p>
""" % (width_attr, height_attr, asset_url, play, quality, param_tags,
       width_attr, height_attr, asset_url, play, quality, param_attrs)

return """
<p class="p">
<object %s%s data="%s" type="application/x-shockwave-flash">
  <param name="movie" value="%s" />
  <param name="play" value="%s" />
  <param name="quality" value="%s" />%s
</object>
</p>
""" % (width_attr, height_attr, asset_url,
       asset_url, play, quality, param_tags)
