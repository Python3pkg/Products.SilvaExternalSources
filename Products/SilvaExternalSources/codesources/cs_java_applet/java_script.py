##parameters=model, version, code, archive='', codebase='', width, height, params=''

if archive is None:
    archive_attr = ''
else:
    archive_url = archive.absolute_url()
    archive_attr = 'archive="%s"' % archive_url

if codebase== '':
    codebase_attr = ''
else:
    codebase_url = codebase.absolute_url()
    codebase_attr = 'codebase="%s"' % codebase_url

param_tags = ''
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
        param_tags = param_tags + '  <param name="' + name \
                + '" value="' + value + '" />\n'


return """
<p class="p">
<applet code="%s" %s%s width="%s" height="%s" align="baseline">
%s  No Java Applet supported!!
</applet>
</p>
""" % (code, archive_attr, codebase_attr, width, height, param_tags)
