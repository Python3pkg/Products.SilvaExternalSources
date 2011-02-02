configuration = {
    'cs_rich_text': {
        'id': 'cs_rich_text',
        'title': 'Rich Text',
        'render_id': 'render',
        'desc': "Rich Text (html) using Tiny MCE",
        'cacheable': False,
        'elaborate': False,
   },
    'cs_page_asset': {
        'id': 'cs_page_asset',
        'title': 'Embed Page Asset',
        'render_id': 'render',
        'desc': "Embed a Page Asset",
        'cacheable': False,
        'elaborate': False,
    },
    'cs_you_tube': {
        'id': 'cs_you_tube',
        'title': 'YouTube video',
        'render_id': 'youtube_source',
        'desc': "Code Source to embed YouTube videos",
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_google_calendar': {
        'id': 'cs_google_calendar',
        'title': 'Google Calendar',
        'render_id': 'google_calendar_source',
        'desc': 'Code Source to embed a public Google Calendar.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_toc': {
        'id': 'cs_toc',
        'title': 'TOC',
        'render_id': 'toc',
        'desc': 'Displays a listing of items contained in folders and/or publications. Multiple listings are possible. This code source replaces the TOC element',
        'cacheable': False,
        'elaborate': False,
        'previewable': True,
    },
    'cs_citation': {
        'id': 'cs_citation',
        'title': 'citation',
        'render_id': 'render_citation',
        'desc': 'A citation allows authors to include a reference, citing an author and a source.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_google_maps': {
        'id': 'cs_google_maps',
        'title': 'Code Source Google Maps iFrame',
        'render_id': 'google_maps_source',
        'desc': 'Code Source for Google Maps iFrame.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_network_image': {
        'id': 'cs_network_image',
        'title': 'Network Image',
        'render_id': 'netimage',
        'desc': 'Insert an image from the network with a link and/or tooltip.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_ms_video': {
        'id': 'cs_ms_video',
        'title': 'MS Video',
        'render_id': 'video_script',
        'desc': 'Embeds a Window Media Player movie.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_quicktime': {
        'id': 'cs_quicktime',
        'title': 'Quicktime',
        'render_id': 'video_script',
        'desc': 'Embedder for a Quicktime movie with configuration parameters.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_related_info': {
        'id': 'cs_related_info',
        'title': 'Related info',
        'render_id': 'capsule',
        'desc': 'Provide related info and crosslinks.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_flash': {
        'id': 'cs_flash',
        'title': 'Flash',
        'render_id': 'flash_script',
        'desc': 'Embeds a Flash movie in a page using parameters.',
        'cacheable': False,
        'elaborate': False,
        'previewable': False,
    },
    'cs_encaptionate': {
        'id': 'cs_encaptionate',
        'title': 'Encaptionated image',
        'render_id': 'capsule',
        'desc': 'Insert an image with title, link, caption, and/or credit.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_java_applet': {
        'id': 'cs_java_applet',
        'title': 'Java Applet',
        'render_id': 'java_script',
        'desc': 'Embeds a Java applet with parameters using the HTML applet tag.',
        'cacheable': True,
        'elaborate': False,
        'previewable': False,
    },
    'cs_java_plugin': {
        'id': 'cs_java_plugin',
        'title': 'Java Plugin',
        'render_id': 'java_script',
        'desc': 'Embeds a Java applet with the Java plug-in mechanism.',
        'cacheable': True,
        'elaborate': False,
        'previewable': False,
    },
    'cs_search_field': {
        'id': 'cs_search_field',
        'title': 'Search Field',
        'render_id': 'layout',
        'desc': 'Inserts a search field in a document. Requires SilvaFind.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_flash_source': {
        'id': 'cs_flash_source',
        'title': 'Flash Source',
        'render_id': 'embedder',
        'desc': 'This Code Source embeds a Flash file (swf or flv) in a page and provides a form for easy parameter configuration.',
        'cacheable': True,
        'elaborate': False,
        'previewable': False,
    },
    'cs_portlet_element': {
        'id': 'cs_portlet_element',
        'title': 'Portlet Element',
        'render_id': 'portlet_element',
        'desc': 'Code Source to include Silva Documents within other Silva Documents.',
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
    'cs_vimeo': {
        'id': 'cs_vimeo',
        'title': 'Vimeo video',
        'render_id': 'vimeo_script',
        'desc': "Code Source to embed Vimeo videos",
        'cacheable': True,
        'elaborate': False,
        'previewable': True,
    },
}
