# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.tests.SilvaTestCase import SilvaFunctionalTestCase
from Products.Silva.tests.SilvaBrowser import SilvaBrowser

CODE_SOURCES = {'cs_encaptionate':{
                    'name': 'Encaptionated image',
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
                    'name': 'Flash',
                    'script_id': 'flash_script',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'flash_script'],
                    'parameters': ['params', 'play', 'quality', 'ref', 'width']},
                'cs_flash_source':{
                    'name': 'Flash Source',
                    'script_id': 'embedder',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'AC_RunActiveContent', 'embedder'],
                    'parameters': ['bgcolor', 'height', 'loop', 'quality',
                                   'type', 'url', 'width']},
                'cs_google_calendar':{
                    'name': 'Google Calendar',
                    'script_id': 'google_calendar_source',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'google_calendar_source'],
                    'parameters': ['calendar_height', 'calendar_title',
                                   'calendar_width', 'google_calendar_account',
                                   'google_calendar_type']},
                'cs_google_maps':{
                    'name': 'Code Source Google Maps iFrame',
                    'script_id': 'google_maps_source',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'google_maps_source', 'iframe_validator'],
                    'parameters': ['iframe']},
                'cs_java_applet':{
                    'name': 'Java Applet',
                    'script_id': 'java_script',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'java_script'],
                    'parameters': ['code', 'codebase', 'height', 'params', 'width']},
                'cs_java_plugin':{
                    'name': 'Java Plugin',
                    'script_id': 'java_script',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'java_script'],
                    'parameters': ['archive', 'code', 'codebase', 'height',
                                   'params', 'width']},
                'cs_ms_video':{
                    'name': 'MS Video',
                    'script_id': 'video_script',
                    'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                                 'video_script'],
                    'parameters': ['autoplay', 'controller', 'height', 'ref',
                                   'width']},
                'cs_toc':{
                    'name': 'TOC',
                    'script_id': 'toc',
                    'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                                 'toc_sort_on', 'toc'],
                    'parameters': ['capsule_title', 'css_class', 'css_style',
                                   'depth', 'display_headings', 'toc_types',
                                   'link_headings', 'paths', 'show_desc',
                                   'sort_on', 'show_icon']},
                'cs_network_image':{
                    'name': 'Network Image',
                    'script_id': 'netimage',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'netimage'],
                    'parameters': ['alignment_selector', 'alt_text',
                                   'image_height', 'image_location',
                                   'image_width', 'link_tooltip', 'link_url']},
                'cs_portlet_element':{
                    'name': 'Portlet Element',
                    'script_id': 'portlet_element',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'get_portlet_content', 'portlet_element'],
                    'parameters': ['alignment_selector', 'capsule_class',
                                   'capsule_id', 'capsule_style',
                                   'capsule_title', 'document', 'show_title']},
                'cs_quicktime':{
                    'name': 'Quicktime',
                    'script_id': 'video_script',
                    'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                                 'video_script'],
                    'parameters': ['autoplay', 'controller', 'height', 'params',
                                   'ref', 'width']},
                'cs_related_info':{
                    'name': 'Related info',
                    'script_id': 'capsule',
                    'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                                 'capsule'],
                    'parameters': ['alignment', 'capsule_body', 'capsule_title',
                                   'css_class', 'css_style', 'link_text',
                                   'link_url']},
                'cs_search_field':{
                    'name': 'Search Field',
                    'script_id': 'layout',
                    'contents': ['HISTORY', 'LICENSE', 'README', 'version',
                                 'layout'],
                    'parameters': ['default_text', 'find_object', 'width']},
                'cs_you_tube':{
                    'name': 'YouTube video',
                    'script_id': 'youtube_source',
                    'contents': ['HISTORY',  'LICENSE',  'README', 'version',
                                 'youtube_source'],
                    'parameters': ['youtube_height', 'youtube_url',
                                   'youtube_width']}
                }

class ManagerCodeSourcesTest(SilvaFunctionalTestCase):
    """ test the install_code_sources method
    """

    def test_manager_codesources(self):
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        self.failUnless(status, 200)

        sb.go('http://nohost/root/manage_services')
        self.failUnless('Code Sources' in sb.browser.contents)
        sb.click_href_labeled('service_codesources (Code Sources)')
        self.failUnless('Silva Code Source Service' in sb.browser.contents)

        # test existence of core silva codesources

        for cs in CODE_SOURCES:
            self.failUnless(cs in sb.browser.contents)

            sb.click_href_labeled(cs)

            cs_script_id = sb.browser.getControl(name='script_id')
            self.assertEquals(cs_script_id.value, CODE_SOURCES[cs]['script_id'])

            cs_name = sb.browser.getControl(name='title')
            self.assertEquals(cs_name.value, CODE_SOURCES[cs]['name'])

            sb.go('http://nohost/root/service_codesources/%s/parameters/manage_main' % (cs))
            self.failUnless('Formulator Form' in sb.browser.contents)
            for parameter in CODE_SOURCES[cs]['parameters']:
                self.failUnless(parameter in sb.browser.contents)
            sb.browser.goBack()

            sb.go('http://nohost/root/service_codesources/%s/manage_main' % (cs))
            self.failUnless('Silva Code Source' in sb.browser.contents)
            for content in CODE_SOURCES[cs]['contents']:
                self.failUnless(content in sb.browser.contents)
            sb.browser.goBack()

            sb.browser.goBack()

        sb.go('http://nohost/root/service_extensions/manage_extensions')
        # uninstall Silva External Sources
        form = sb.browser.getForm(name='SilvaExternalSources')
        form.getControl('deactivate').click()
        self.failUnless('SilvaExternalSources uninstalled' in sb.browser.contents)
        sb.go('http://nohost/root/manage_workspace')
        # click into the Silva instance
        sb.click_href_labeled('Silva /edit...')
        self.failUnless('&#xab;root&#xbb;' in sb.browser.contents)
        # logout
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerCodeSourcesTest))
    return suite
