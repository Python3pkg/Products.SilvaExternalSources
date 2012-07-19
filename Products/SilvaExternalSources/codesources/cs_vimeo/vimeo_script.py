##parameters=REQUEST, model, version, vimeo_id, width, height

return """
<iframe src="http://player.vimeo.com/video/%(video_id)s" width="%(video_width)s" height="%(video_height)s" frameborder="0"></iframe>
""" % {"video_id": vimeo_id,
       "video_width": width,
       "video_height": height}
