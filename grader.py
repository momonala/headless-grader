# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
from datetime import datetime
from itertools import permutations
from tkinter import Tk

from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from credentials import credentials


class Grader:
    def __init__(self, web_browser, verbose=True, log=True):
        creds = credentials()

        self.browser = web_browser
        self.verbose = verbose
        self.log = log
        self.start = time.time()
        self.perms = permutations(range(1, 7), 4)

        # FOR LOGIN ROUTINE
        self.start_page = 'https://auth.udacity.com/sign-in?next=https%3A%2F%2Fmentor-dashboard.udacity.com%2Freviews%2Foverview'
        self.email_xpath = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div/form/div/div[1]/input'
        self.pass_xpath = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div/form/div/div[2]/input'
        self.email = creds['email']
        self.password = creds['password']
        self.signin_button_xpath = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div/form/button'
        self.queue_status_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div[1]/div[1]/h3'
        self.queue_enter_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div/div[2]/button'
        self.queue_full_xpath = '/html/body/div[2]/div/div/div/section/div/div/div/div[2]/label'
        self.queue_now_xpath = '/html/body/div[2]/div/div/div/section/div/footer/button'
        self.queue_refresh_button_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div[2]/button'

        # CHECK IF GRADING ML OR WEB
        self.ml_project = None

        # FOR GETTING PENDING PROJECTS FROM THE DASHBOARD
        self.project_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/section[1]/div/ul/li/div[4]/a'
        self.time_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div[2]/section[1]/div/ul/li/div[3]/div[2]/p'

        # FOR SWITCHING TABS INSIDE GRADING
        self.code_tab_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[3]'
        self.review_tab_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[4]'
        # '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[3]/a'

        # FOR HTML VALIDATION
        self.html_validation_page = 'https://validator.w3.org/#validate_by_input'
        self.html_input_xpath = '//*[@id="fragment"]'
        self.html_check_button_xpath = '/html/body/div[2]/div/fieldset[3]/form/p[2]/a'
        self.html_val_results_xpath = '//*[@id="results"]'

        # FOR SELECTING CODE IN THE EDITOR
        self.code_body_CSS_selector = '.CodeMirror-code > div:nth-child(1)'

        # FOR FINAL SUBMISSION
        self.submit_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/footer/div/div/button'
        self.confirm_xpath = '/html/body/div[1]/div/div/div/form/div[2]/div/button'

        # FINAL TEXT SECTION
        self.final_text_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/ng-form/div/div/div[1]/div/div/textarea'
        self.final_save_button_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/ng-form/div/div/div[2]/div/button[1]'

        # FOR HOLDING RAW CODE AS A LIST
        self.html = None
        self.CSS = None

        # GRADE BOOLEANS
        self.has_code = False
        self.html_validation = False
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

    @staticmethod
    def sleep(seconds=4):
        # utility function to wait for pages to render
        time.sleep(seconds)

    def _scroll_into_view(self, e):
        # scroll an element into view
        self.browser.execute_script("return arguments[0].scrollIntoView();", e)

    def find_by_xpath_click(self, xpath):
        e = self.browser.find_element(By.XPATH, xpath)
        self._scroll_into_view(e)
        e.click()

    def login(self):
        # a simple login routine
        self.browser.get(self.start_page)
        self.browser.find_element(By.XPATH, self.email_xpath).send_keys(self.email)
        self.browser.find_element(By.XPATH, self.pass_xpath).send_keys(self.password)
        self.browser.find_element(By.XPATH, self.signin_button_xpath).click()
        self.sleep(6)
        print('Login Sucessful!') if self.verbose else 0

    def refresh_queue(self):
        # check if we're in queue or not, and enter/refresh accordingly
        queue_status = self.browser.find_element(By.XPATH, self.queue_status_xpath).text
        if queue_status == 'Queue Off':
            self.browser.find_element(By.XPATH, self.queue_enter_xpath).click()
            self.sleep(3)
            self.browser.find_element(By.XPATH, self.queue_full_xpath).click()
            self.browser.find_element(By.XPATH, self.queue_now_xpath).click()
        else:
            self.browser.find_element(By.XPATH, self.queue_refresh_button_xpath).click()
        print('Queue Refresh Sucessful!') if self.verbose else 0

    def check_if_ml(self):
        # check if its an ML project or not, set state.
        e = self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/h1')
        if e.text == 'Use a Pre-trained Image Classifier to Identify Dog Breeds':
            self.ml_project = True
            print('Grading ML Project') if self.verbose else 0
        else:
            self.ml_project = False
            print('Grading Intro to Web Project') if self.verbose else 0

    def get_project(self):
        # Open the new project, wait, then switch control to new tab
        try:
            time_remaining = self.browser.find_element(By.XPATH, self.time_xpath).text
            if 'minutes' not in time_remaining:
                time_remaining = int(time_remaining.split(' ')[0])
                if time_remaining > 7:
                    # print('Project available but too soon to grade.')
                    return False

            self.browser.find_element(By.XPATH, self.project_xpath).click()
            self.sleep(4)
            print('Accessed new project!') if self.verbose else 0
            self.browser.switch_to_window(self.browser.window_handles[1])
            self.sleep(4)
            self.check_if_ml()
            return True

        except NoSuchElementException:
            print('No projects to grade') if self.verbose else 0
            return False

    def _get_code_tab(self):
        # in project, get the code tab where we can read code
        self.browser.find_element(By.XPATH, self.code_tab_xpath).click()

    def _get_preview_tab(self):
        # in project, get the preview tab where we can grade
        self.browser.find_element(By.XPATH, self.review_tab_xpath).click()

    # ------------------------------- WEB ----------------------------------------------------
    def _check_files(self):
        # go to code review tab, check for HTML and CSS files
        self._get_code_tab()
        self.code_files_tab = 'code-section-item-title'
        self.code_files = self.browser.find_elements(By.CLASS_NAME, self.code_files_tab)

        self.html_page = None
        self.CSS_page = None
        self.has_html = False
        self.has_CSS = False
        for i, file_ in enumerate(self.code_files):
            if '.html' in file_.get_attribute('innerHTML').lower():
                self.has_html = True
                self.html_page = self.code_files[i]
            if '.css' in file_.get_attribute('innerHTML').lower():
                self.has_CSS = True
                self.CSS_page = self.code_files[i]
        if self.has_CSS is True and self.has_html is True:
            self.has_code = True
        print('Intial File Analysis Complete!') if self.verbose else 0

    def _copy_code(self, lang):
        # open the current code tab and copy to the clipboard
        if lang == 'html':
            page = self.html_page
        elif lang == 'css':
            page = self.CSS_page
        else:
            raise ValueError('Error in copying! Wrong file type!')

        self._scroll_into_view(page)
        page.click()
        self.sleep(1)
        element = self.browser.find_element(By.CSS_SELECTOR, self.code_body_CSS_selector)
        self._scroll_into_view(element)
        self.sleep(2)
        ActionChains(self.browser)\
            .click(element) \
            .key_down(Keys.CONTROL) \
            .key_down('a') \
            .key_up('a') \
            .key_down('c') \
            .key_up('c') \
            .key_up(Keys.CONTROL) \
            .perform()
        print('Copied {}!'.format(lang)) if self.verbose else 0

    def _validate_html(self):
        # head over the HTML validator and look for errors
        self.browser.execute_script("$(window.open('{}'))".format(self.html_validation_page))
        self.sleep()
        self.browser.switch_to_window(self.browser.window_handles[2])
        html_input = self.browser.find_element(By.XPATH, self.html_input_xpath)
        ActionChains(self.browser)\
            .click(html_input) \
            .key_down(Keys.CONTROL) \
            .key_down('v') \
            .key_up(Keys.CONTROL) \
            .key_up('v') \
            .perform()

        self.browser.find_element(By.XPATH, self.html_check_button_xpath).click()
        self.sleep(3)

        results = self.browser.find_element(By.XPATH, self.html_val_results_xpath)

        if 'No errors or warnings to show' in results.text:
            self.html_validation = True
            print('Student passed HTML!') if self.verbose else 0
        else:
            self.html_validation = False
            print('Student failed HTML!') if self.verbose else 0
            self.html_val_error_msgs = []
            for line in results.text.split('\n'):
                line = line.split('.')
                for subline in line:
                    if 'Error' in subline:
                        self.html_val_error_msgs.append('\n\n' + subline)

        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[1])
        print('HTML Validation Complete!') if self.verbose else 0

    def _read_html(self):
        # read the HTML from the clipboard and analyze
        html_raw = Tk().clipboard_get()
        html = html_raw.split('\n')
        for line in html:
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
            print(f'divs: {self.divs} \nh-tags: {self.h} \nimg: {self.has_img} \n'
                  f'link: {self.has_link} \nlinked-CSS: {self.has_linked_CSS} \nCSS class {self.has_CSS_class}')

    def _read_css(self):
        # read the CSS from the clipboard and analyze
        css_raw = Tk().clipboard_get()
        css = css_raw.split('\n')
        for line in css:
            if "{" in line:
                self.num_CSS_selectors += 1
        if self.num_CSS_selectors >= 3:
            self.has_CSS_selectors = True

        if self.verbose:
            print('CSS selectors: {} Passed {}'.format(self.num_CSS_selectors, self.has_CSS_selectors))

    def _grade_web_section(self, section, criteria, pass_msg, fail_msg):
        # grade a single section based on a criteria, XPATH template below
        #       '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[SEC]/div/div/ng-form/div[PASS-FAIL]/div/label/input'
        _fail1 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[1]/div/label/input'
        _pass1 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[2]/div/label/input'
        _text1 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text2 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[4]/div[1]/div/div/textarea'
        _save1 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save2 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[2]/div[2]/div/button[1]'
        _save3 = f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div[{section}]/div/div/ng-form/div[4]/div[2]/div/button[1]'

        if criteria is True:
            _grade = _pass1
            msg = pass_msg
        else:
            _grade = _fail1
            msg = fail_msg

        try:
            # click the pass or fail button for this section
            # grading for the 1st time, or 2nd time and failed before
            self.find_by_xpath_click(_grade)

            try:
                # first time grading
                e = self.browser.find_element(By.XPATH, _text1)
                self._scroll_into_view(e)
                e.send_keys(msg)
                self.find_by_xpath_click(_save1)
                return
            except NoSuchElementException:
                # second time grading, failed previously
                e = self.browser.find_element(By.XPATH, _text2)
                self._scroll_into_view(e)
                e.send_keys(msg)
                self.find_by_xpath_click(_save3)
                return

        except NoSuchElementException:
            # already graded and passed, somtimes finicky about XPATH...
            try:
                self.find_by_xpath_click(_save1)
                return
            except NoSuchElementException:
                self.find_by_xpath_click(_save2)
                return

    def _grade_web_section_first9(self):
        # Grade the first 9 sections of a web project (10th is different format).
        pass_msg = "Both files were found, great work!"
        fail_msg = "Either CSS or HTML file was missing :("
        self._grade_web_section(1, self.has_code, pass_msg, fail_msg)

        pass_msg = "Nice job with the linked CSS!"
        fail_msg = "You need to use linked CSS to pass this part :("
        self._grade_web_section(2, self.has_linked_CSS, pass_msg, fail_msg)

        pass_msg = "You passed the validations, great work!"
        fail_msg = ("Unfortunately you did not pass the validation. Specfically, "
                    "I found the errors below. Keep in mind that though page can still render to your browser, "
                    "there may be validation issues. If left unsolved, your code may eventually fail on different browsers. "
                    "Please ask check out the study groups or discussion forums if you need help solving these errors. "
                    "Good luck!\n{}").format(self.html_val_error_msgs)
        self._grade_web_section(3, self.html_validation, pass_msg, fail_msg)

        pass_msg = "Great work with the header tags! You know your stuff :)"
        fail_msg = ("Please make sure you have the corrent number of header tags, "
                    "which is at least 3. See this link to learn more: https://www.w3schools.com/tags/tag_header.asp")
        self._grade_web_section(4, self.has_headers, pass_msg, fail_msg)

        pass_msg = 'Great work using the div tags!'
        fail_msg = 'Please make sure you have the corrent number of div tags, which is at least 3. See this link to learn more: https://www.w3schools.com/Tags/tag_div.asp'
        self._grade_web_section(5, self.has_divs, pass_msg, fail_msg)

        pass_msg = "Nice work using the CSS Selectors! You've demonstrated some solid knowledge on these."
        fail_msg = ("Please make sure you have the corrent number of CSS Selectors, which is at least 3. "
                    "Please check out https://www.w3schools.com/cssref/css_selectors.asp for more info")
        self._grade_web_section(6, self.has_CSS_selectors, pass_msg, fail_msg)

        pass_msg = 'Nice work with the CSS selectors!'
        fail_msg = 'Please make sure you use CSS class selectors! Please see https://www.w3schools.com/cssref/css_selectors.asp if you are have trouble.'
        self._grade_web_section(7, self.has_CSS_class, pass_msg, fail_msg)

        pass_msg = "Great work using img tags, you've demonstrated some solid knowledge!"
        fail_msg = " Unfortunately you did not pass this section. Please see https://www.w3schools.com/tags/tag_img.asp if you are having difficulty with using image tags."
        self._grade_web_section(8, self.has_img, pass_msg, fail_msg)

        pass_msg = "Great work using links!"
        fail_msg = "Please see https://www.w3schools.com/html/html_links.asp if you are having difficulty with images"
        self._grade_web_section(9, self.has_link, pass_msg, fail_msg)

        print('sections 1-9 graded!') if self.verbose else 0

    def _grade_web_section_last(self):
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
            self.find_by_xpath_click(_grade)
            e = self.browser.find_element(By.XPATH, _text1)
            self._scroll_into_view(e)
            e.send_keys(msg)
            self.find_by_xpath_click(_save1)
        except NoSuchElementException:
            # if already graded - two options...
            try:
                self.find_by_xpath_click(_save3)
            except NoSuchElementException:
                self.find_by_xpath_click(_save2)

    def _fill_final_text_section_web(self):
        # fill out the final section of text (good job message)
        self.all_sections = [self.has_code,
                             self.html_validation,
                             self.has_img,
                             self.has_link,
                             self.has_linked_CSS,
                             self.has_headers,
                             self.has_divs,
                             self.has_CSS_class,
                             self.has_CSS_selectors]
        if False in self.all_sections:
            msg = ("Great work on this project so far! You're almost there. "
                   "Please try to fix the errors above. If you need personal help, "
                   "please check out the study groups or discussion forums (https://knowledge.udacity.com/). "
                   "And good luck on the resubmission!")
        else:
            msg = ('Great work! This was a nice project with clean code, '
                   'and you demonstrated a clear knowledge of HTML and CSS. '
                   'Onward to  the next project! Additionally, if you have any feedback on how I can improve, '
                   'let me know! Thanks')
        e = self.browser.find_element(By.XPATH, self.final_text_xpath)
        self._scroll_into_view(e)
        e.send_keys(msg)
        e = self.browser.find_element(By.XPATH, self.final_save_button_xpath)
        e.click()

    def _submit_project(self):
        # submit the graded project!
        self.find_by_xpath_click(self.submit_xpath)
        self.sleep(2)
        self.find_by_xpath_click(self.confirm_xpath)
        print('Project Submitted!') if self.verbose else 0

    def _did_pass(self):
        # set state for passing
        if False in [self.has_code,
                     self.html_validation,
                     self.has_img,
                     self.has_link,
                     self.has_linked_CSS,
                     self.has_headers,
                     self.has_divs,
                     self.has_CSS_class,
                     self.has_CSS_selectors]:
            return False
        else:
            return True

    def _grade_web_project(self):
        # grade the damn project!
        self.start = time.time()
        self._check_files()
        self._copy_code('html')
        self._validate_html()
        self._read_html()
        self._copy_code('css')
        self._read_css()

        self._get_preview_tab()
        self._grade_web_section_first9()
        self._grade_web_section_last()
        self._fill_final_text_section_web()
        self._submit_project()

    # ---------------------------- ML -------------------------------------------
    def grade_ml_section(self, button_x, text_x, save_x, msg, save_x2_li=list(), section=None):
        """ Grade an ML section. If already graded, iterate through a list of high probablity save xpaths.
        If that fails, iterate throuhg every possible permutation, given our knowledge about how the
        paths are formatted (brute force). """
        try:
            self.find_by_xpath_click(button_x)
            e = self.browser.find_element(By.XPATH, text_x)
            self._scroll_into_view(e)
            e.send_keys(msg)
            self.find_by_xpath_click(save_x)
            return

        # if we're here, then this section has likely already been graded
        except NoSuchElementException:
            for x in save_x2_li:
                try:
                    self.find_by_xpath_click(x)
                    return
                except NoSuchElementException:
                    pass
            if section not in [1, 13]:
                print(f'Predefined XPATHS failed for section {section}. Attemping loop.')
                p = self._grade_arbitrary_ml_section()
                print(f'section:{section} - {p} worked!')
            else:
                print(f'Predefined XPATHS for section {section} failed.')

    @staticmethod
    def _get_arbitrary_xpath(w, x, y, z):
        # Generate an xpath for an arbitrary section save.
        return f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[{w}]/div/div/div[{x}]/div[{y}]/div/div/ng-form/div[{z}]/div[2]/div/button[1]'

    def _grade_arbitrary_ml_section(self):
        # Grade an arbitrary section or throw an error if failure.
        for p in self.perms:
            xpath = self._get_arbitrary_xpath(*p)
            if xpath not in self.known_xpaths:
                try:
                    self.find_by_xpath_click(xpath)
                    return p
                except NoSuchElementException:
                    pass
        raise InvalidSelectorException('New or unknown xpath for this section!')

    def _grade_all_ml_sections(self):

        # button to enter text area
        _button_x1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div/div/div/ng-form/div[2]/div/label/input'
        _button_x2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[1]/div/div/ng-form/div[2]/div/label/input'
        _button_x3 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div/ng-form/div[2]/div/label/input'
        _button_x4 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div/ng-form/div[2]/div/label/input'
        _button_x5 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div/ng-form/div[2]/div/label/input'
        _button_x6 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[2]/div/div/ng-form/div[2]/div/label/input'
        _button_x7 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[3]/div/div/ng-form/div[2]/div/label/input'
        _button_x8 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[1]/div/div/ng-form/div[2]/div/label/input'
        _button_x9 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[2]/div/div/ng-form/div[2]/div/label/input'
        _button_x10 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[3]/div/div/ng-form/div[2]/div/label/input'
        _button_x11 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div/ng-form/div[2]/div/label/input'
        _button_x12 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[5]/div/div/div[2]/div[2]/div/div/ng-form/div[2]/div/label/input'
        _button_x13 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[6]/div/div/div[2]/div/div/div/ng-form/div[2]/div/label/input'

        # text field
        _text_x1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x3 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x4 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x5 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x6 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x7 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[3]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x8 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x9 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x10 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[3]/div/div/ng-form/div[4]/div[1]/div/div/textarea'
        _text_x11 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x12 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[5]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[1]/div/div/textarea'
        _text_x13 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[6]/div/div/div[2]/div/div/div/ng-form/div[3]/div[1]/div/div/textarea'

        # save button
        _save_x1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x3 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x4 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div/ng-form/div[2]/div[2]/div/button[1]'
        _save_x5 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x6 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x7 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[3]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x8 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x9 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x10 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/div/div/div[2]/div[3]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x11 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x12 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[5]/div/div/div[2]/div[2]/div/div/ng-form/div[3]/div[2]/div/button[1]'
        _save_x13 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[6]/div/div/div[2]/div/div/div/ng-form/div[3]/div[2]/div/button[1]'

        # message to student
        msg_1 = "Great work making use of the time function here. This is a really useful tool to both manipulate the user experience and to check on the performance of your projects, especially as they scale in size and complexity."
        msg_2 = "Excellent work adding the --dir command line argument! This allows the user to change the working directory as and when required, and doesn't limit them to using just one specified directory."
        msg_3 = "Same goes for the --arch CLI. You've demonstrated good knowledge of this!"
        msg_4 = "Nice job with the --dogfile CLI"
        msg_5 = "Great work ignoring certain file types!"
        msg_6 = "Brilliant job building the dog label dictionary! This was a tricky part of the project, and proves you have the skills to manipulate data (filenames) to produce a given format, no matter how much the filenames themselves differ. Well done!"
        msg_7 = "Nice - you've passed in the arguments retrieved from the user (via arg parsing, the defaults are used if the user doesn't specify anything) and passed them correctly to the get_pet_labels function."
        msg_8 = "Great work here in passing the image directory (the argument obtained using the arg_parser as specified by the user, of by the default argument), the key (filename) and the model architecture to the classifier function. Just to recap this bit - this function then makes calls to the pre-trained image classifier neural network which has been trained on millions of images to learn how to predict what the images you pass to it are."
        msg_9 = "Formatting looks good!"
        msg_10 = "Good job here too - We're now directly comparing what the AI model thinks the image is of to what the truth is (in this project, remember we've said that the true values are the manipulated file names). Well done!"
        msg_11 = "Good stuff - all matches between the true labels (i.e. adjusted filenames) and the AI classifier labels are correctly categorised."
        msg_12 = "All the displayed outputs match up and are appropriately displayed, good job. "
        msg_13 = "Brilliant - all model outputs score as expected. Well done."

        # if the project has already been graded
        x1_save1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div/div/div/ng-form/div[2]/div[2]/div/button[1]'
        x1_save2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div/div/div/ng-form/div[3]/div[2]/div/button[1]'
        x1_save3 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[1]/div/div/div[2]/div/div/div/ng-form/div[4]/div[2]/div/button[1]'

        x6_save1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[3]/div/div/div[2]/div[2]/div/div/ng-form/div[2]/div[2]/div/button[1]'

        x13_save1 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[6]/div/div/div[2]/div/div/div/ng-form/div[3]/div[2]/div/button[1]'
        x13_save2 = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[6]/div/div/div[2]/div/div/div/ng-form/div[2]/div[2]/div/button[1]'

        x1 = [x1_save1, x1_save2, x1_save3]
        x2 = [self._get_arbitrary_xpath(2, 2, 1, 2), self._get_arbitrary_xpath(2, 2, 1, 3)]
        x3 = [self._get_arbitrary_xpath(2, 2, 2, 2), self._get_arbitrary_xpath(2, 2, 2, 3)]
        x4 = [self._get_arbitrary_xpath(2, 2, 3, 2), self._get_arbitrary_xpath(2, 2, 3, 3)]
        x5 = [self._get_arbitrary_xpath(3, 2, 1, 2), self._get_arbitrary_xpath(3, 2, 1, 4)]
        x6 = [self._get_arbitrary_xpath(3, 2, 2, 3), self._get_arbitrary_xpath(3, 2, 3, 2), self._get_arbitrary_xpath(3, 2, 2, 2), x6_save1]
        x7 = [self._get_arbitrary_xpath(3, 2, 3, 2), self._get_arbitrary_xpath(3, 2, 3, 3), self._get_arbitrary_xpath(4, 2, 1, 2), self._get_arbitrary_xpath(4, 2, 1, 3)]
        x8 = [self._get_arbitrary_xpath(4, 2, 1, 3), self._get_arbitrary_xpath(4, 2, 2, 2), self._get_arbitrary_xpath(4, 2, 3, 2), self._get_arbitrary_xpath(4, 2, 2, 3)]
        x9 = [self._get_arbitrary_xpath(4, 2, 2, 2), self._get_arbitrary_xpath(5, 2, 1, 2), self._get_arbitrary_xpath(4, 2, 3, 3)]
        x10 = [self._get_arbitrary_xpath(4, 2, 3, 4), self._get_arbitrary_xpath(4, 2, 3, 2), self._get_arbitrary_xpath(4, 2, 3, 3), self._get_arbitrary_xpath(5, 2, 2, 2)]
        x11 = [self._get_arbitrary_xpath(5, 2, 1, 2), self._get_arbitrary_xpath(5, 2, 1, 3), self._get_arbitrary_xpath(5, 2, 1, 4), self._get_arbitrary_xpath(4, 2, 2, 3)]
        x12 = [self._get_arbitrary_xpath(5, 2, 2, 4), self._get_arbitrary_xpath(5, 2, 2, 2), self._get_arbitrary_xpath(5, 2, 2, 3), self._get_arbitrary_xpath(6, 2, 1, 3)]
        x13 = [x13_save1, x13_save2]
        self.known_xpaths = [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x12]

        self.grade_ml_section(_button_x1, _text_x1, _save_x1, msg_1, x1, 1)
        self.grade_ml_section(_button_x2, _text_x2, _save_x2, msg_2, x2, 2)
        self.grade_ml_section(_button_x3, _text_x3, _save_x3, msg_3, x3, 3)
        self.grade_ml_section(_button_x4, _text_x4, _save_x4, msg_4, x4, 4)
        self.grade_ml_section(_button_x5, _text_x5, _save_x5, msg_5, x5, 5)
        self.grade_ml_section(_button_x6, _text_x6, _save_x6, msg_6, x6, 6)
        self.grade_ml_section(_button_x7, _text_x7, _save_x7, msg_7, x7, 7)
        self.grade_ml_section(_button_x8, _text_x8, _save_x8, msg_8, x8, 8)
        self.grade_ml_section(_button_x9, _text_x9, _save_x9, msg_9, x9, 9)
        self.grade_ml_section(_button_x10, _text_x10, _save_x10, msg_10, x10, 10)
        self.grade_ml_section(_button_x11, _text_x11, _save_x11, msg_11, x11, 11)
        self.grade_ml_section(_button_x12, _text_x12, _save_x12, msg_12, x12, 12)
        self.grade_ml_section(_button_x13, _text_x13, _save_x13, msg_13, x13, 13)

    def _fill_final_section_ml(self):
        # senf the final message about the whole project to the student.
        msg = "Awesome work on this project! You've demonstrated a solid understanding of using ML classifiers within Python. Onward to the next project!"
        final_text_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[8]/ng-form/div/div/div[1]/div/div/textarea'
        final_save_button_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[8]/ng-form/div/div/div[2]/div/button[1]'

        e = self.browser.find_element(By.XPATH, final_text_xpath)
        self._scroll_into_view(e)
        e.send_keys(msg)
        self.browser.find_element(By.XPATH, final_save_button_xpath).click()

    def _grade_ml(self):
        # grade all ml projects
        self._get_preview_tab()
        self._grade_all_ml_sections()
        self._fill_final_section_ml()
        self._submit_project()

    # -----------------------------------------------------------------------------

    def _write_logs(self):
        # send logs to file
        proj_type = 'ML' if self.ml_project else 'web'
        output = f'\n{str(datetime.now())} \tgraded {proj_type} project in {"{0:.2f}".format(time.time() - self.start)}s \tpassing: {self._did_pass()}'
        print(output)
        with open('grades.txt', 'a') as f:
            f.write(output)

    def grade_project(self):
        # determine if ML or web, and grade!
        if self.ml_project:
            self._grade_ml()
        else:
            self._grade_web_project()
        if self.log:
            self._write_logs()


def launch_browser(headless=False, timeout=4):
    """Launch a Firefox webdriver with disabled notifications,
        allow page loading, optionally phantom mode

    Args:
        headless (bool): if True, launch in phantom/headless mode,
                        where you cannot see the browser (default=False)
        timeout (int): time (s) to wait for a response (default=10)
    Returns:
        Webdriver (object): Firefox. With firefox profile settings
                            as explained above.
    """
    # https://stackoverflow.com/questions/32953498/how-can-i-remove-notifications-and-alerts-from-browser-selenium-python-2-7-7
    # https://stackoverflow.com/questions/26566799/how-to-wait-until-the-page-is-loaded-with-selenium-for-python
    # https://stackoverflow.com/questions/5370762/how-to-hide-firefox-window-selenium-webdriver
    # https://developer.mozilla.org/en-US/Firefox/Headless_mode#Selenium-in-Python

    options = Options()
    if headless:
        options.add_argument('-headless')

    fp = FirefoxProfile()
    fp.set_preference("dom.webnotifications.enabled", False)
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.getcwd())
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                      "application/zip")

    web_browser = Firefox(firefox_profile=fp,
                          executable_path='geckodriver',
                          firefox_options=options)
    web_browser.implicitly_wait(timeout)
    return web_browser


if __name__ == '__main__':
    browser = launch_browser()

    headless_grader = Grader(browser)
    headless_grader.login()
    headless_grader.refresh_queue()

    if headless_grader.get_project():
        headless_grader.grade_project()

    headless_grader.sleep(3)
    headless_grader.browser.quit()
