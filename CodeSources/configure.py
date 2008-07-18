# XXX this conf needs settings for "Source is cachable" and "Source is elaborate".
# Both cs_YouTube and cs_GoogleCalendar are cachable.

configuration = {
    'cs_you_tube': {
        'id': 'cs_you_tube',
        'title': 'YouTube video',
        'render_id': 'youtube_source',
        'desc': "Code Source to embed YouTube videos",
        'cacheable': True,
        'elaborate': False,
    },
    'cs_google_calendar': {
        'id': 'cs_google_calendar',
        'title': 'Google Calendar',
        'render_id': 'google_calendar_source',
        'desc': 'Code Source to embed a public Google Calendar.',
        'cacheable': True,
        'elaborate': False,
    },
    'cs_multitoc': {
        'id': 'cs_multitoc',
        'title': 'MultiTOC',
        'render_id': 'multi_toc',
        'desc': 'Displays a listing of items contained in folders and/or publications.',
        'cacheable': False,
        'elaborate': False,
    },
}
