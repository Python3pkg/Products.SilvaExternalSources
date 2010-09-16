# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


CODE_SOURCES = {
    'cs_encaptionate': {
        'title': 'Encaptionated image',
        'script_id': 'capsule',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'capsule'],
        'parameters': ['alignment_selector', 'alt_text',
                       'capsule_style', 'capsule_title',
                       'caption_text', 'credit_link',
                       'credit_prefix', 'credit_text',
                       'creditlink_tooltip', 'image_link',
                       'image_path', 'link_tooltip', 'link_url']},
    'cs_flash':{
        'title': 'Flash',
        'script_id': 'flash_script',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'flash_script'],
        'parameters': ['params', 'play', 'quality', 'ref', 'width']},
    'cs_flash_source':{
        'title': 'Flash Source',
        'script_id': 'embedder',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'AC_RunActiveContent', 'embedder'],
        'parameters': ['bgcolor', 'height', 'loop', 'quality',
                       'type', 'url', 'width']},
    'cs_google_calendar':{
        'title': 'Google Calendar',
        'script_id': 'google_calendar_source',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'google_calendar_source'],
        'parameters': ['calendar_height', 'calendar_title',
                       'calendar_width', 'google_calendar_account',
                       'google_calendar_type']},
    'cs_google_maps':{
        'title': 'Code Source Google Maps iFrame',
        'script_id': 'google_maps_source',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'google_maps_source', 'iframe_validator'],
        'parameters': ['iframe']},
    'cs_java_applet':{
        'title': 'Java Applet',
        'script_id': 'java_script',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'java_script'],
        'parameters': ['code', 'codebase', 'height', 'params', 'width']},
    'cs_java_plugin':{
        'title': 'Java Plugin',
        'script_id': 'java_script',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'java_script'],
        'parameters': ['archive', 'code', 'codebase', 'height',
                       'params', 'width']},
    'cs_ms_video':{
        'title': 'MS Video',
        'script_id': 'video_script',
        'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                     'video_script'],
        'parameters': ['autoplay', 'controller', 'height', 'ref',
                       'width']},
    'cs_toc':{
        'title': 'TOC',
        'script_id': 'toc',
        'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                     'toc_sort_on', 'toc'],
        'parameters': ['capsule_title', 'css_class', 'css_style',
                       'depth', 'display_headings', 'toc_types',
                       'link_headings', 'paths', 'show_desc',
                       'sort_on', 'show_icon']},
    'cs_network_image':{
        'title': 'Network Image',
        'script_id': 'netimage',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'netimage'],
        'parameters': ['alignment_selector', 'alt_text',
                       'image_height', 'image_location',
                       'image_width', 'link_tooltip', 'link_url']},
    'cs_portlet_element':{
        'title': 'Portlet Element',
        'script_id': 'portlet_element',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'get_portlet_content', 'portlet_element'],
        'parameters': ['alignment_selector', 'capsule_class',
                       'capsule_id', 'capsule_style',
                       'capsule_title', 'document', 'show_title']},
    'cs_quicktime':{
        'title': 'Quicktime',
        'script_id': 'video_script',
        'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                     'video_script'],
        'parameters': ['autoplay', 'controller', 'height', 'params',
                       'ref', 'width']},
    'cs_related_info':{
        'title': 'Related info',
        'script_id': 'capsule',
        'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                     'capsule'],
        'parameters': ['alignment', 'capsule_body', 'capsule_title',
                       'css_class', 'css_style', 'link_text',
                       'link_url']},
    'cs_search_field':{
        'title': 'Search Field',
        'script_id': 'layout',
        'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                     'layout'],
        'parameters': ['default_text', 'find_object', 'width']},
    'cs_you_tube':{
        'title': 'YouTube video',
        'script_id': 'youtube_source',
        'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                     'youtube_source'],
        'parameters': ['youtube_height', 'youtube_url',
                       'youtube_width']}
    }

class ManagerCodeSourcesTest(unittest.TestCase):
    """ test the install_code_sources method
    """
    layer = FunctionalLayer

    def test_service(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        self.assertEqual(browser.get_link('manage...').click(), 200)
        self.assertEqual(browser.location, '/root/manage_main')

        self.assertEqual(browser.inspect.zmi_tabs['Services'].click(), 200)
        self.assertEqual(browser.location, '/root/manage_services')

        self.assertEqual(
            browser.inspect.zmi_listing['service_codesources'].click(),
            200)
        self.assertEqual(
            browser.inspect.zmi_title,
            ['Silva Code Source Service'])

        # test existence of core silva codesources
        for source_name in CODE_SOURCES:
            info = CODE_SOURCES[source_name]

            self.assertTrue(source_name in browser.inspect.zmi_listing)
            self.assertEqual(
                browser.inspect.zmi_listing[source_name].click(),
                200)

            form = browser.get_form('editform')
            for fieldname in ['title', 'script_id']:
                self.assertEqual(
                    form.get_control(fieldname).value,
                    info[fieldname],
                    msg='Wrong value %s for %s in %s' % (
                        form.get_control(fieldname).value, fieldname, source_name))

            self.assertEqual(browser.get_link('manage parameters').click(), 200)
            for parameter in info['parameters']:
                self.assertTrue(
                    parameter in browser.inspect.zmi_listing,
                    msg='Missing parameter %s in %s' % (parameter, source_name))

            self.assertEqual(browser.get_link(source_name).click(), 200)
            self.assertEqual(browser.get_link('manage contents').click(), 200)

            for content in info['contents']:
                self.assertTrue(
                    content in browser.inspect.zmi_listing,
                    msg='Missing content %s in %s' % (content, source_name))

            self.assertEqual(
                browser.get_link('service_codesources').click(),
                200)

    def test_uninstall(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        self.assertEqual(browser.get_link('manage...').click(), 200)
        self.assertEqual(browser.location, '/root/manage_main')

        self.assertEqual(browser.inspect.zmi_tabs['Services'].click(), 200)
        self.assertEqual(browser.location, '/root/manage_services')

        self.assertEqual(
            browser.inspect.zmi_listing['service_extensions'].click(),
            200)

        # Uninstall Silva External Sources
        form = browser.get_form('SilvaExternalSources')
        self.assertEqual(form.get_control('uninstall').click(), 200)
        self.assertEqual(
            browser.inspect.zmi_feedback,
            ['SilvaExternalSources uninstalled'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerCodeSourcesTest))
    return suite
