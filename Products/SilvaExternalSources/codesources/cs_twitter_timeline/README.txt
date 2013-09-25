README for Twitter Widget Code Source
=====================================

This README should reside inside a Silva Code Source named 'cs_twitter_timeline'.
The Code Source allows to place a configurable Twitter Timeline Widget in a document.
In order to use this CS you have to first create a Twitter widget in your profile
and then input the widget ID in this CS (https://twitter.com/settings/widgets/new).
This widget ID is the value of the "data-widget-id" attribute in the HTML code
that Twitter provides you after saving the widget in your profile.

Customizing the Twitter CS
--------------------------
You can set many parameters to customize the Twitter Widget but only two of them
are required: the Twitter Username and the Widget ID. Here follows a brief description
of each parameter you can set:

- Username: your Twitter username
- Widget ID: the value of the "data-widget-id" attribute in the HTML code Twitter
    provides you after saving the widget in your profile.
- Height: the height of the Twitter widget (units are pixels).
- Theme: light or dark widget theme.
- Chrome: the widget layout, you can use a space-separated set of the following options:
    - noheader: hides the timeline header.
    - nofooter: hides the timeline footer and Tweet box, if included.
    - noborders: removes all borders within the widget.
    - noscrollbar: crops and hides the main timeline scrollbar, if visible.
    - transparent: removes the background color.
- Tweet limit: this is to fix the size of a timeline to a preset number of Tweets.
- Link color: the link color used by the widget. Use the hexadecimal notation.
- Border color: the border color used by the widget. Use the hexadecimal notation.

Optional Twitter Card
---------------------
The Twitter Card is not strictly related with this Twitter CS
but it might be a useful feature you might want to consider in addition
to displaying the Twitter timeline widget.
For more info:
https://dev.twitter.com/docs/cards
https://dev.twitter.com/docs/cards/validation/validator
