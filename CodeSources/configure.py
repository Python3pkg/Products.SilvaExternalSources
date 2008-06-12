# XXX this conf needs settings for "Source is cachable" and "Source is elaborate".
# Both cs_YouTube and cs_GoogleCalendar are cachable.

configuration = {
    'cs_YouTube': {
        'id': 'cs_youtube',
        'dirname': 'cs_YouTube',
        'title': 'YouTube video',
        'render_id': 'youtube_source',
        'desc': "Code Source to embed YouTube videos",
        'form': 'parameters.xml',
        'script_id': None,
        'script_body': None,
        'template_id': 'youtube_source',
        'template_body': 'youtube_source.pt',
        'history': 'HISTORY.txt',
        'license': 'LICENSE.txt',
        'readme': 'README.txt',
        'version': 'version.txt',
    },
    'cs_GoogleCalendar': {
        'id': 'cs_google_calendar',
        'dirname': 'cs_GoogleCalendar',
        'title': 'Google Calendar',
        'render_id': 'google_calendar_source',
        'desc': 'Code Source to embed a public Google Calendar.',
        'form': 'parameters.xml',
        'script_id': None,
        'script_body': None,
        'template_id': 'google_calendar_source',
        'template_body': 'google_calendar_source.pt',
        'history': 'HISTORY.txt',
        'license': 'LICENSE.txt',
        'readme': 'README.txt',
        'version': 'version.txt',
    },
    'cs_MultiTOC': {
        'id': 'cs_multitoc',
        'dirname': 'cs_MultiTOC',
        'title': 'MultiTOC',
        'render_id': 'multi_toc',
        'desc': 'Displays a listing of items contained in folders and/or publications.',
        'form': 'parameters.xml',
        'script_id': 'sort_tree',
        'script_body': 'sort_tree.py',
        'template_id': 'multi_toc',
        'template_body': 'multi_toc.pt',
        'history': 'HISTORY.txt',
        'license': 'LICENSE.txt',
        'readme': 'README.txt',
        'version': 'version.txt',
    },
    'cs_GoogleMaps': {
        'id': 'cs_google_maps',
        'dirname': 'cs_GoogleMaps',
        'title': 'Code Source Google Maps iFrame',
        'render_id': 'google_maps_source',
        'desc': 'Code Source for Google Maps iFrame.',
        'form': 'parameters.xml',
        'script_id': 'iframe_validatory',
        'script_body': 'iframe_validator.py',
        'template_id': 'google_maps_source',
        'template_body': 'google_maps_source.pt',
        'history': 'HISTORY.txt',
        'license': 'LICENSE.txt',
        'readme': 'README.txt',
        'version': 'version.txt',
    },
    'cs_NetworkImage': {
        'id': 'cs_network_image',
        'dirname': 'cs_NetworkImage',
        'title': 'Network Image',
        'render_id': 'netimage',
        'desc': 'Insert an image from the network with a link and/or tooltip.',
        'form': 'parameters.xml',
        'script_id': None,
        'script_body': None,
        'template_id': 'netimage',
        'template_body': 'netimage.pt',
        'history': 'HISTORY.txt',
        'license': 'LICENSE.txt',
        'readme': 'README.txt',
        'version': 'version.txt',
    },

}
