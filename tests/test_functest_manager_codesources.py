import unittest
from Products.Silva.tests.SilvaTestCase import SilvaFunctionalTestCase
from Products.Silva.tests.SilvaBrowser import SilvaBrowser


CODE_SOURCES = {'cs_google_calendar': {'name': 'Google Calendar', 'script_id': 'google_calendar'},
                'cs_youtube': {},
                'cs_multitoc': {},}

class ManagerCodeSourcesTest(SilvaFunctionalTestCase):
    """ test the install_code_sources method
    """
    def test_manager_codesources(self):
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        self.failUnless(status, 200)
        sb.go('http://nohost/manage_main')
        self.failUnless('Control_Panel (Control Panel)' in sb.browser.contents)
        # click Silva root
        sb.go('http://nohost/root/manage_workspace')
        self.failUnless('Silva /edit...' in sb.browser.contents)
        # click services tab
        sb.click_href_labeled('Services')
        self.failUnless('service_extensions (Silva Product and Extension Configuration)' in sb.browser.contents)
        # click service_extensions
        sb.click_href_labeled('service_extensions (Silva Product and Extension Configuration)')
        self.failUnless('Configure Silva Extension Products' in sb.browser.contents)
        # install Silva External Sources
        form = sb.browser.getForm(name="SilvaExternalSources")
        form.getControl('activate').click()
        self.failUnless('SilvaExternalSources installed' in sb.browser.contents)
        sb.go('http://nohost/root/manage_services')
        self.failUnless('Code Sources' in sb.browser.contents)
        sb.click_href_labeled('service_codesources (Code Sources)')
        # test existence of core silva codesources
        for cs in CODE_SOURCES.keys():
            self.failUnless(cs in sb.browser.contents)
        # test the cs_google_calendar codesource
        sb.click_href_labeled('cs_google_calendar')
        self.failUnless('Google Calendar' in sb.browser.contents)
        script_id = sb.browser.getControl(name='script_id')
        self.assertEquals(script_id.value, 'google_calendar_source')
        sb.click_href_labeled('manage contents')
        self.failUnless('HISTORY.txt' in sb.browser.contents)
        self.failUnless('LICENSE.txt' in sb.browser.contents)
        self.failUnless('README.txt' in sb.browser.contents)
        self.failUnless('google_calendar_source' in sb.browser.contents)
        self.failUnless('version.txt' in sb.browser.contents)
        sb.browser.goBack()
        sb.click_href_labeled('manage parameters')
        self.failUnless('calendar_background_color' in sb.browser.contents)
        self.failUnless('calendar_height' in sb.browser.contents)
        self.failUnless('calendar_title' in sb.browser.contents)
        self.failUnless('calendar_width' in sb.browser.contents)
        self.failUnless('google_calendar_account' in sb.browser.contents)
        self.failUnless('google_calendar_type' in sb.browser.contents)
        sb.browser.goBack()
        sb.go('http://nohost/root/service_codesources/manage_main')
        # test the cs_youtube codesource
        sb.click_href_labeled('cs_youtube')
        self.failUnless('YouTube video' in sb.browser.contents)
        script_id = sb.browser.getControl(name='script_id')
        self.assertEquals(script_id.value, 'youtube_source')
        sb.click_href_labeled('manage contents')
        self.failUnless('HISTORY.txt' in sb.browser.contents)
        self.failUnless('LICENSE.txt' in sb.browser.contents)
        self.failUnless('README.txt' in sb.browser.contents)
        self.failUnless('youtube_source' in sb.browser.contents)
        self.failUnless('version.txt' in sb.browser.contents)
        sb.browser.goBack()
        sb.click_href_labeled('manage parameters')
        self.failUnless('youtube_height' in sb.browser.contents)
        self.failUnless('youtube_url' in sb.browser.contents)
        self.failUnless('youtube_width' in sb.browser.contents)
        sb.browser.goBack()
        sb.go('http://nohost/root/service_codesources/manage_main')
        # test the multitoc codesource
        sb.click_href_labeled('cs_multitoc')
        self.failUnless('MultiTOC' in sb.browser.contents)
        script_id = sb.browser.getControl(name='script_id')
        self.assertEquals(script_id.value, 'multi_toc')
        sb.click_href_labeled('manage contents')
        self.failUnless('HISTORY.txt' in sb.browser.contents)
        self.failUnless('LICENSE.txt' in sb.browser.contents)
        self.failUnless('README.txt' in sb.browser.contents)
        self.failUnless('multi_toc' in sb.browser.contents)
        self.failUnless('sort_tree' in sb.browser.contents)
        self.failUnless('version.txt' in sb.browser.contents)
        sb.browser.goBack()
        sb.click_href_labeled('manage parameters')
        self.failUnless('alignment' in sb.browser.contents)
        self.failUnless('capsule_title' in sb.browser.contents)
        self.failUnless('css_class' in sb.browser.contents)
        self.failUnless('css_style' in sb.browser.contents)
        self.failUnless('depth' in sb.browser.contents)
        self.failUnless('display_title' in sb.browser.contents)
        self.failUnless('filter_meta_types' in sb.browser.contents)
        self.failUnless('link_title' in sb.browser.contents)
        self.failUnless('paths' in sb.browser.contents)
        self.failUnless('public' in sb.browser.contents)
        self.failUnless('sort_on' in sb.browser.contents)
        self.failUnless('sort_order' in sb.browser.contents)
        sb.go('http://nohost/root/service_extensions/manage_editForm')
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
