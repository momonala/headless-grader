from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import os
import re
from tkinter import Tk
from credentials import credentials


class Grader:
    def __init__(self, browser, verbose=True):
        creds = credentials()

        self.browser = browser
        self.verbose = verbose

        # FOR LOGIN ROUTINE
        self.start_page = 'https://auth.udacity.com/sign-in?next=https%3A%2F%2Fmentor-dashboard.udacity.com%2Freviews%2Foverview'
        self.email_XPATH = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div/form/div/div[1]/input'
        self.pass_XPATH = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div/form/div/div[2]/input'
        self.email = creds['email']
        self.password = creds['password']
        self.signin_button_XPATH = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div/form/button'
        self.queue_status_XPATH = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div[1]/div[1]/h3'
        self.queue_enter_XPATH = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div/div[2]/button'
        self.queue_full_XPATH = '/html/body/div[2]/div/div/div/section/div/div/div/div[2]/label'
        self.queue_now_XPATH = '/html/body/div[2]/div/div/div/section/div/footer/button'
        self.queue_refresh_button_XPATH = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div[2]/button'

        # FOR GETTING PENDING PROJECTS FROM THE DASHBOARD
        self.project_XPATH = '/html/body/div[1]/div/div/div[1]/div[2]/div/section[1]/div/ul/li/div[4]/a'

        # FOR SWITCHING TABS INSIDE GRADING
        self.code_tab_XPATH = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[3]'
        self.review_tab_XPATH = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[4]'

        # FOR HTML VALIDATION
        self.HTML_validation_page = 'https://validator.w3.org/#validate_by_input'
        self.HTML_input_XPATH = '//*[@id="fragment"]'
        self.HTML_check_button_XPATH = '/html/body/div[2]/div/fieldset[3]/form/p[2]/a'
        self.HTML_val_results_XPATH = '//*[@id="results"]'

        # FOR SELECTING CODE IN THE EDITOR
        self.code_body_CSS_selector = '.CodeMirror-code > div:nth-child(1)'

        # FOR FINAL SUBMISSION
        self.submit_XPATH = '/html/body/div[2]/div/div[2]/div/div[2]/div/footer/div/div/button'
        self.confirm_XPATH = '/html/body/div[1]/div/div/div/form/div[2]/div/button'

        # FINAL TEXT SECTION
        self.final_text_XPATH = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/ng-form/div/div/div[1]/div/div/textarea'
        self.final_save_button_XPATH = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/ng-form/div/div/div[2]/div/button[1]'

        # FOR HOLDING RAW CODE AS A LIST
        self.HTML = None
        self.CSS = None

        # GRADE BOOLEANS
        self.has_code = False
        self.HTML_validation = False
        self.has_img = False
        self.has_link = False
        self.has_linked_CSS = False
        self.has_headers = False
        self.has_divs = False
        self.has_CSS_class = False
        self.has_CSS_selectors = False
        self.divs = 0
        self.h = 0
        self.num_CSS_selectors = 0

        self.html_val_error_msgs = None

    def SLEEP(self, seconds=4):
        # utility function to wait for pages to render
        time.sleep(seconds)

    def scroll_into_view(self, e):
        # scroll an element into view
        self.browser.execute_script("return arguments[0].scrollIntoView();", e)

    def login(self):
        # a simple login routine
        self.browser.get(self.start_page)
        self.browser.find_element(By.XPATH, self.email_XPATH).send_keys(self.email)
        self.browser.find_element(By.XPATH, self.pass_XPATH).send_keys(self.password)
        self.browser.find_element(By.XPATH, self.signin_button_XPATH).click()
        self.SLEEP(6)
        print('Login Sucessful!') if self.verbose else 0

    def refresh_queue(self):
        # check if we're in queue or not, and enter/refresh accordingly
        queue_status = self.browser.find_element(By.XPATH, self.queue_status_XPATH).text
        if queue_status == 'Queue Off':
            self.browser.find_element(By.XPATH, self.queue_enter_XPATH).click()
            self.SLEEP(3)
            self.browser.find_element(By.XPATH, self.queue_full_XPATH).click()
            self.browser.find_element(By.XPATH, self.queue_now_XPATH).click()
        else:
            self.browser.find_element(By.XPATH, self.queue_refresh_button_XPATH).click()
        print('Queue Refresh Sucessful!') if self.verbose else 0

    def get_project(self):
        # open the new project, wait, then switch control to new tab
        try:
            self.browser.find_element(By.XPATH, self.project_XPATH).click()
            self.SLEEP(4)
            print('Accessed new project!') if self.verbose else 0
            self.browser.switch_to_window(self.browser.window_handles[1])
            self.SLEEP(4)
            return True

        except NoSuchElementException as e:
            print('No projects to grade') if self.verbose else 0
            return False

    def get_code_tab(self):
        # in project, get the code tab where we can read code
        self.browser.find_element(By.XPATH, self.code_tab_XPATH).click()

    def get_preview_tab(self):
        # in project, get the preview tab where we can grade
        self.browser.find_element(By.XPATH, self.review_tab_XPATH).click()

    def check_files(self):
        # go to code review tab, check for HTML and CSS files
        self.get_code_tab()
        self.code_files_tab = 'code-section-item-title'
        self.code_files = self.browser.find_elements(By.CLASS_NAME, self.code_files_tab)

        self.HTML_page = None
        self.CSS_page = None
        self.has_HTML = False
        self.has_CSS = False
        for i, file_ in enumerate(self.code_files):
            if '.html' in file_.get_attribute('innerHTML').lower():
                self.has_HTML = True
                self.HTML_page = self.code_files[i]
            if '.css' in file_.get_attribute('innerHTML').lower():
                self.has_CSS = True
                self.CSS_page = self.code_files[i]
        if self.has_CSS is True and self.has_HTML is True:
            self.has_code = True
        print('Intial File Analysis Complete!') if self.verbose else 0

    def copy_code(self, lang):
        # open the current code tab and copy to the clipboard
        if lang == 'html':
            page = self.HTML_page
        elif lang == 'css':
            page = self.CSS_page
        else:
            print('Error in copying! Wrong file type!') if self.verbose else 0

        self.scroll_into_view(page)
        page.click()
        self.SLEEP(1)
        element = self.browser.find_element(By.CSS_SELECTOR, self.code_body_CSS_selector)
        self.scroll_into_view(element)
        self.SLEEP(2)
        ActionChains(self.browser) \
                     .click(element) \
                     .key_down(Keys.CONTROL) \
                     .key_down('a') \
                     .key_up('a') \
                     .key_down('c') \
                     .key_up('c') \
                     .key_up(Keys.CONTROL) \
                     .perform()
        print('Copied {}!'.format(lang)) if self.verbose else 0

    def validate_HTML(self):
        # head over the HTML validator and look for errors
        self.browser.execute_script("$(window.open('{}'))".format(self.HTML_validation_page))
        self.SLEEP()
        self.browser.switch_to_window(self.browser.window_handles[2])
        HTML_input = self.browser.find_element(By.XPATH, self.HTML_input_XPATH)
        ActionChains(self.browser) \
                     .click(HTML_input) \
                     .key_down(Keys.CONTROL) \
                     .key_down('v') \
                     .key_up(Keys.CONTROL) \
                     .key_up('v') \
                     .perform()

        self.browser.find_element(By.XPATH, self.HTML_check_button_XPATH).click()
        self.SLEEP(3)

        results = self.browser.find_element(By.XPATH, self.HTML_val_results_XPATH)

        if 'No errors or warnings to show' in results.text:
            self.HTML_validation = True
            print('Student passed HTML!') if self.verbose else 0
        else:
            self.HTML_validation = False
            print('Student failed HTML!') if self.verbose else 0
            self.html_val_error_msgs = []
            for line in results.text.split('\n'):
                line = line.split('.')
                for subline in line:
                    if 'Error' in subline:
                        self.html_val_error_msgs.append('\n\n'+subline)

        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[1])
        print('HTML Validation Complete!') if self.verbose else 0

    def read_HTML(self):
        # read the HTML from the clipboard and analyze
        html_raw = Tk().clipboard_get()
        HTML = html_raw.split('\n')
        for line in HTML:
            if '<img src= ' and 'alt=' in line:
                self.has_img = True
            if '<div' in line:
                self.divs += 1
            if re.match('<h[0-9]+', line.strip()) is not None:
                self.h += 1
            if '<link' in line:
                self.has_linked_CSS = True
            if '<a' in line:
                self.has_link = True
            if 'class' in line:
                self.has_CSS_class = True
        if self.divs >= 3:
            self.has_divs = True
        if self.h >= 3:
            self.has_headers = True
        if self.verbose:
            print('divs: {} \nh-tags: {} \nimg: {} \nlink: {} \nlinked-CSS: {} \nCSS class {}'.
                  format(self.divs, self.h, self.has_img, self.has_link,
                         self.has_linked_CSS, self.has_CSS_class))

    def read_CSS(self):
        # read the CSS from the clipboard and analyze
        css_raw = Tk().clipboard_get()
        CSS = css_raw.split('\n')
        for line in CSS:
            if "{" in line:
                self.num_CSS_selectors += 1
        if self.num_CSS_selectors >= 3:
            self.has_CSS_selectors = True

        if self.verbose:
            print('CSS selectors: {} passed {}'.format(self.num_CSS_selectors,
                                                       self.has_CSS_selectors))

    def grade_section(self, section, criteria, pass_msg, fail_msg):
        # grade a single section based on a criteria, XPATH template below
        #       '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[SEC]/div/div/ng-form/div[PASS-FAIL]/div/label/input'
        _fail1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[1]/div/label/input'.format(section)
        _pass1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[2]/div/label/input'.format(section)

        _text1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[3]/div[1]/div/div/textarea'.format(section)
        _text2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[4]/div[1]/div/div/textarea'.format(section)

        _save1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[3]/div[2]/div/button[1]'.format(section)
        _save2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[2]/div[2]/div/button[1]'.format(section)
        _save3 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{}]/div/div/ng-form/div[4]/div[2]/div/button[1]'.format(section)

        if criteria is True:
            _grade = _pass1
            msg = pass_msg
        else:
            _grade = _fail1
            msg = fail_msg

        try:
            # click the pass or fail button for this section
            # grading for the 1st time, or 2nd time and failed before
            e = self.browser.find_element(By.XPATH, _grade)
            self.scroll_into_view(e)
            e.click()

            try:
                # first time grading
                e = self.browser.find_element(By.XPATH, _text1)
                self.scroll_into_view(e)
                e.send_keys(msg)
                e = self.browser.find_element(By.XPATH, _save1)
                self.scroll_into_view(e)
                e.click()
                return 1
            except NoSuchElementException as e:
                # second time grading, failed previously
                e = self.browser.find_element(By.XPATH, _text2)
                self.scroll_into_view(e)
                e.send_keys(msg)
                e = self.browser.find_element(By.XPATH, _save3)
                self.scroll_into_view(e)
                e.click()
                return 1

        except NoSuchElementException as e:
            # already graded and passed, somtimes finicky about XPATH...
            try:
                e = self.browser.find_element(By.XPATH, _save1)
                self.scroll_into_view(e)
                e.click()
                return 1
            except NoSuchElementException as e:
                e = self.browser.find_element(By.XPATH, _save2)
                self.scroll_into_view(e)
                e.click()
                return 1

    def grade_section_FIRST9(self):
        pass_msg = 'Both files found, great work!'
        fail_msg = 'Either CSS or HTML file was missing :('
        self.grade_section(1, self.has_code, pass_msg, fail_msg)

        pass_msg = 'Nice job with the linked CSS!'
        fail_msg = 'You need to use linked CSS to pass this part :('
        self.grade_section(2, self.has_linked_CSS, pass_msg, fail_msg)

        pass_msg = 'You passed the validations, great work!'
        fail_msg = 'Unfortunately you did not pass the validation. Specfically,\
                    I found the errors below. Please ask your mentor if you\
                    need help solving these errors. \
                    Good luck!\n{}'.format(self.html_val_error_msgs)
        self.grade_section(3, self.HTML_validation, pass_msg, fail_msg)

        pass_msg = 'Great work using the header tags!'
        fail_msg = 'Please make sure you have the corrent number of header\
                    tags, which is at least 3. See this link to learn more:\
                    https://www.w3schools.com/tags/tag_header.asp'
        self.grade_section(4, self.has_headers, pass_msg, fail_msg)

        pass_msg = 'Great work using the div tags!'
        fail_msg = 'Please make sure you have the corrent number of div tags,\
                    which is at least 3. See this link to learn more:\
                    https://www.w3schools.com/Tags/tag_div.asp'
        self.grade_section(5, self.has_divs, pass_msg, fail_msg)

        pass_msg = 'Nice work using the CSS Selectors!\
                    Youve demonstrated some solid knowledge on these.'
        fail_msg = 'Please make sure you have the corrent number of CSS\
                    Selectors, which is at least 3. Please check out\
                    https://www.w3schools.com/cssref/css_selectors.asp\
                    for more info'
        self.grade_section(6, self.has_CSS_selectors, pass_msg, fail_msg)

        pass_msg = 'Nice work with the CSS selectors!'
        fail_msg = 'Please make sure you use CSS class selectors! Please\
                    see https://www.w3schools.com/cssref/css_selectors.asp\
                    for more'
        self.grade_section(7, self.has_CSS_class, pass_msg, fail_msg)

        pass_msg = 'Great work using the img tags!'
        fail_msg = 'Please see https://www.w3schools.com/tags/tag_img.asp\
                    if you are having difficulty with images'
        self.grade_section(8, self.has_img, pass_msg, fail_msg)

        pass_msg = 'Great work using the links!'
        fail_msg = 'Please see https://www.w3schools.com/html/html_links.asp\
                    if you are having difficulty with images'
        self.grade_section(9, self.has_link, pass_msg, fail_msg)

        print('sections 1-9 graded!') if self.verbose else 0

    def grade_section_LAST(self):
        # last (section 10) must be different for some reason...
        criteria = True
        pass_msg = 'Great work!'
        fail_msg = 'Please make sure to credit your work'

        _fail1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div/div/div/ng-form/div[1]/div/label/input'
        _pass1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div/div/div/ng-form/div[2]/div/label/input'
        _text1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div/div/div/ng-form/div[3]/div[1]/div/div/textarea'

        _save1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div/div/div/ng-form/div[2]/div[2]/div/button[1]'
        _save3 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div/div/div/ng-form/div[4]/div[2]/div/button[1]'
        if criteria is True:
            _grade = _pass1
            msg = pass_msg
        else:
            _grade = _fail1
            msg = fail_msg

        try:
            # if not graded before
            e = self.browser.find_element(By.XPATH, _grade)
            self.scroll_into_view(e)
            e.click()
            e = self.browser.find_element(By.XPATH, _text1)
            self.scroll_into_view(e)
            e.send_keys(msg)
            e = self.browser.find_element(By.XPATH, _save1)
            self.scroll_into_view(e)
            e.click()
        except NoSuchElementException:
            # if already graded - two options...
            try:
                e = self.browser.find_element(By.XPATH, _save3)
                self.scroll_into_view(e)
                e.click()
            except NoSuchElementException:
                e = self.browser.find_element(By.XPATH, _save2)
                self.scroll_into_view(e)
                e.click()

    def fill_final_text_section(self):
        # fill out the final section of text (good job message)
        self.all_sections = [self.has_code,
                             self.HTML_validation,
                             self.has_img,
                             self.has_link,
                             self.has_linked_CSS,
                             self.has_headers,
                             self.has_divs,
                             self.has_CSS_class,
                             self.has_CSS_selectors]
        if False in self.all_sections:
            msg = "Great work on this project so far! You're almost there.\
             Please try to fix the errors above, and good luck on the \
             resubmission!"
        else:
            msg = "Great work! This was a nice project with clean code,\
             and you demonstrated a clear knowledge of HTML and CSS. Onward to\
             the next project!"
        e = self.browser.find_element(By.XPATH, self.final_text_XPATH)
        self.scroll_into_view(e)
        e.send_keys(msg)
        self.browser.find_element(By.XPATH, self.final_save_button_XPATH).click()

    def submit_project(self):
        # submit the graded project!
        self.browser.find_element(By.XPATH, self.submit_XPATH).click()
        self.SLEEP(2)
        self.browser.find_element(By.XPATH, self.confirm_XPATH).click()
        print('Project Submitted!') if self.verbose else 0

    def grade_project(self):
        # grade the damn project!
        start = time.time()
        self.check_files()
        self.copy_code('html')
        self.validate_HTML()
        self.read_HTML()
        self.copy_code('css')
        self.read_CSS()

        self.get_preview_tab()
        self.grade_section_FIRST9()
        self.grade_section_LAST()
        self.fill_final_text_section()
        self.submit_project()
        print('graded project in {0:0.2f}s'.format(time.time()-start))


def launch_browser(phantom=False):
    ''' launch a Firefox webdriver with disabled notifications,
        allow page loading, optionally phantom mode

    Args:
        phantom (bool): if True, launch in phantom/headless mode,
                        where you cannot see the browser (default=False)
    Returns:
        Webdriver (object): Firefox. With firefox profile settings
                            as explained above.
    '''
    # https://stackoverflow.com/questions/32953498/how-can-i-remove-notifications-and-alerts-from-browser-selenium-python-2-7-7
    # https://stackoverflow.com/questions/26566799/how-to-wait-until-the-page-is-loaded-with-selenium-for-python
    # https://stackoverflow.com/questions/5370762/how-to-hide-firefox-window-selenium-webdriver

    if phantom:
        os.environ['MOZ_HEADLESS'] = '1'

    fp = webdriver.FirefoxProfile()
    fp.set_preference("dom.webnotifications.enabled", False)
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.getcwd())
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                      "application/zip")

    browser = webdriver.Firefox(firefox_profile=fp)
    browser.implicitly_wait(10)
    return browser


if __name__ == '__main__':
    # start the session
    browser = launch_browser()

    headless_grader = Grader(browser)
    headless_grader.login()
    headless_grader.refresh_queue()

    if headless_grader.get_project():
        headless_grader.grade_project()

    headless_grader.SLEEP(3)
    headless_grader.browser.quit()
