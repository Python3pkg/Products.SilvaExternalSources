##parameters=ref, controller, autoplay, width='', height=''
# Embeds movies using the Windows Media Player. This Code Source
# was developped to embed *.avi files - therefore it uses the
# clsid of the class ID of the Windows Media Player 6 
# (clsid:05589FA1-C356-11CE-BF01-00AA0055595A) instead of the newer
# ID of the Player versions 7 - 10
# (clsid:6BF52A52-394A-11D3-B153-00C04F79FAA6), which did not work with
# *.avi files. Furthermore it includes 'type="application/x-mplayer2"' in
# the embed tag (the 'video/x-ms-wmv' type would work too, but this Code
# Source explicitely calls for the Windows Media Player). The Windows
# Media Player Plug-in DLL in Firefox does not listen to the extension
# *.avi or its correct MIME-type, 'video/x-msvideo' (or 'video/avi').

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

if controller == 'true':
    embed_controller = '1'
else:
    embed_controller = '0'

if autoplay== 'true':
    embed_autoplay = '1'
else:
    embed_autoplay = '0'

return """
<p class="p">
<object %s%s classid="clsid:05589FA1-C356-11CE-BF01-00AA0055595A">
  <param name="src" value="%s" />
  <param name="autostart" value="%s" />
  <param name="showcontrols" value="%s" />
  <embed %s%ssrc="%s"
    type="application/x-mplayer2" autostart="%s" showcontrols="%s" />
</object>
</p>
""" % (width_attr, height_attr, video_url, autoplay, controller,
       width_attr, height_attr, video_url, embed_autoplay, embed_controller)
