##parameters= vimeo_id, width, height

video_id = vimeo_id
video_width = width
video_height = height

return """
<iframe src="http://player.vimeo.com/video/%(video_id)s" width="%(video_width)s" height="%(video_height)s" frameborder="0"></iframe>
""" % {"video_id":video_id, "video_width":video_width, "video_height":video_height}
