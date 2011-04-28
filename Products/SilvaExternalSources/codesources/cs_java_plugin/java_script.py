##parameters=model, version, code, archive='', codebase='', width, height, params=''
# Creates the HTML code for the java plugin technology according to the
# documentation on
# http://java.sun.com/j2se/1.5.0/docs/guide/plugin/developer_guide/using_tags.html#general
#
# The HTML created here directs the browser to use any installed Java 2
# environment up from version is 1.2.
# Unfortunately I could not find out how to instruct Internet Explorer to use
# the latest installed version from 1.2 on, and at the same time to specify a
# download page with the latest version.

if archive is None:
    archive_param_tag = ''
    archive_attr = ''
else:
    archive_url = archive.absolute_url()
    archive_param_tag = '<param name="archive" value="%s" />' % archive_url
    archive_attr = 'archive="%s"' % archive_url

if codebase is None:
    codebase_param_tag = ''
    codebase_attr = ''
else:
    codebase_url = codebase.absolute_url()
    codebase_param_tag = '<param name="codebase" value="%s" />' % codebase_url
    codebase_attr = 'codebase="%s"' % codebase_url

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
<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93"
  width="%s" height="%s" align="baseline"
  codebase="http://java.sun.com/products/plugin/1.2/jinstall-12-win32.cab#Version=1,2,0,0">
  <param name="code" value="%s" />
  %s%s%s
  <param name="type" value="application/x-java-applet;version=1.2" />
  <embed type="application/x-java-applet;version=1.2"
    width="%s" height="%s" align="baseline"
    code="%s"
    %s%s%s
    pluginspage="http://java.sun.com/j2se/1.5.0/download.html">
    <noembed>
      No Java 2 SDK support!!
    </noembed>
  </embed>
</object>
</p>
""" % (width, height, code, archive_param_tag, codebase_param_tag, param_tags,
           width, height, code, archive_attr, codebase_attr, param_attrs)

return """
<p class="p">
            <!--[if !IE]>-->
            <object classid="java:%s"
                    type="application/x-java-applet"
                    archive="%s"
                    width="%s" height="%s" >
              <!-- Konqueror browser needs the following param -->
              <param name="archive" value="%s" />
            <!--<![endif]-->
              <object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93"
                      width="%s" height="%s" >
                <param name="code" value="%s" />
                <param name="archive" value="%s" />
              </object>
            <!--[if !IE]>-->
            </object>
            <!--<![endif]-->
</p>
""" % (code, archive_url, width, height, archive_url,
       width, height, code, archive_url)

return """
<p class="p">
           <object type="application/x-java-applet"
                   width="%s" height="%s" >
             <param name="code" value="%s" />
             %s%s%s
           </object>
</p>
""" % (width, height, code, archive_param_tag, codebase_param_tag, param_tags)

