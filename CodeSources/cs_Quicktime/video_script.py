##parameters=ref, controller, autoplay, width, height, params=''

model = context.REQUEST.model

if ref.find('://') == -1:
    video = model.restrictedTraverse(str(ref))
    video_url = video.absolute_url()
else:
    video_url = ref

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

return """
<p class="p">
<object %s%s
  classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B"
  codebase="http://www.apple.com/qtactivex/qtplugin.cab">
  <param name="src" value="%s" />
  <param name="autoplay" value="%s" />
  <param name="controller" value="%s" />%s
  <comment>
  <embed %s%sautoplay="%s" controller="%s"
    src="%s"
    pluginspage="http://www.apple.com/quicktime/download/"%s />
  </comment>
</object>
</p>
""" % (width_attr, height_attr, video_url, autoplay, controller, param_tags,
       width_attr, height_attr, autoplay, controller, video_url, param_attrs)
