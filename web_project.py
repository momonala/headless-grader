# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from tkinter import Tk

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebProject:
    def __init__(self):
        # FOR SELECTING FROM THE CODE TAB
        self.code_files = None
        self.code_files_tab = 'code-section-item-title'

        # FOR SELECTING CODE IN THE EDITOR
        self.code_body_CSS_selector = '.CodeMirror-code > div:nth-child(1)'

        # FOR HTML VALIDATION
        self.html_validation_page = 'https://validator.w3.org/#validate_by_input'
        self.html_input_xpath = '//*[@id="fragment"]'
        self.html_check_button_xpath = '/html/body/div[2]/div/fieldset[3]/form/p[2]/a'
        self.html_val_results_xpath = '//*[@id="results"]'

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
        self.has_html = False
        self.html_page = None
        self.has_CSS = False
        self.CSS_page = None
        self.html_val_error_msgs = None

        self.all_sections = None

    def check_files(self, grader):
        # go to code review tab, check for HTML and CSS files
        self.code_files = grader.browser.find_elements(By.CLASS_NAME, self.code_files_tab)

        for i, file_ in enumerate(self.code_files):
            if '.html' in file_.get_attribute('innerHTML').lower():
                self.has_html = True
                self.html_page = self.code_files[i]
            if '.css' in file_.get_attribute('innerHTML').lower():
                self.has_CSS = True
                self.CSS_page = self.code_files[i]
        if self.has_CSS is True and self.has_html is True:
            self.has_code = True
        logger.debug('Intial File Analysis Complete!') if grader.verbose else 0

    def copy_code(self, grader, lang):
        # open the current code tab and copy to the clipboard
        if lang == 'html':
            page = self.html_page
        elif lang == 'css':
            page = self.CSS_page
        else:
            raise ValueError('Error in copying! Wrong file type!')

        grader.scroll_into_view(page)
        page.click()
        grader.sleep(1)
        element = grader.browser.find_element(By.CSS_SELECTOR, self.code_body_CSS_selector)
        grader.scroll_into_view(element)
        grader.sleep(2)
        ActionChains(grader.browser)\
            .click(element) \
            .key_down(Keys.CONTROL) \
            .key_down('a') \
            .key_up('a') \
            .key_down('c') \
            .key_up('c') \
            .key_up(Keys.CONTROL) \
            .perform()
        logger.debug('Copied {}!'.format(lang)) if grader.verbose else 0

    def validate_html(self, grader):
        # head over the HTML validator and look for errors
        grader.browser.execute_script("$(window.open('{}'))".format(self.html_validation_page))
        grader.sleep()
        grader.browser.switch_to_window(grader.browser.window_handles[2])
        html_input = grader.browser.find_element(By.XPATH, self.html_input_xpath)
        ActionChains(grader.browser)\
            .click(html_input) \
            .key_down(Keys.CONTROL) \
            .key_down('v') \
            .key_up(Keys.CONTROL) \
            .key_up('v') \
            .perform()

        grader.browser.find_element(By.XPATH, self.html_check_button_xpath).click()
        grader.sleep(3)

        results = grader.browser.find_element(By.XPATH, self.html_val_results_xpath)

        if 'No errors or warnings to show' in results.text:
            self.html_validation = True
            logger.debug('Student passed HTML!') if grader.verbose else 0
        else:
            self.html_validation = False
            logger.debug('Student failed HTML!') if grader.verbose else 0
            self.html_val_error_msgs = []
            for line in results.text.split('\n'):
                line = line.split('.')
                for subline in line:
                    if 'Error' in subline:
                        self.html_val_error_msgs.append('\n\n' + subline)

        grader.browser.close()
        grader.browser.switch_to_window(grader.browser.window_handles[1])
        logger.debug('HTML Validation Complete!') if grader.verbose else 0

    def read_html(self, grader):
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
        if grader.verbose:
            logger.debug(f'divs: {self.divs} \nh-tags: {self.h} \nimg: {self.has_img} \n'
                         f'link: {self.has_link} \nlinked-CSS: {self.has_linked_CSS} \n'
                         f'CSS class {self.has_CSS_class}')

    def read_css(self, grader):
        # read the CSS from the clipboard and analyze
        css_raw = Tk().clipboard_get()
        css = css_raw.split('\n')
        for line in css:
            if "{" in line:
                self.num_CSS_selectors += 1
        if self.num_CSS_selectors >= 3:
            self.has_CSS_selectors = True

        if grader.verbose:
            logger.debug('CSS selectors: {} Passed {}'.format(self.num_CSS_selectors, self.has_CSS_selectors))

    @staticmethod
    def _grade_web_section(grader, section, criteria, pass_msg, fail_msg):
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
            grader.find_by_xpath_click(_grade)

            try:
                # first time grading
                e = grader.browser.find_element(By.XPATH, _text1)
                grader.scroll_into_view(e)
                e.send_keys(msg)
                grader.find_by_xpath_click(_save1)
            except NoSuchElementException:
                # second time grading, failed previously
                e = grader.browser.find_element(By.XPATH, _text2)
                grader.scroll_into_view(e)
                e.send_keys(msg)
                grader.find_by_xpath_click(_save3)

        except NoSuchElementException:
            # already graded and passed, somtimes finicky about XPATH...
            try:
                grader.find_by_xpath_click(_save1)
            except NoSuchElementException:
                grader.find_by_xpath_click(_save2)

    def grade_web_section_first9(self, grader):
        # Grade the first 9 sections of a web project (10th is different format).
        pass_msg = "Both files were found, great work!"
        fail_msg = "Either CSS or HTML file was missing :("
        self._grade_web_section(grader, 1, self.has_code, pass_msg, fail_msg)

        pass_msg = "Nice job with the linked CSS!"
        fail_msg = "You need to use linked CSS to pass this part :("
        self._grade_web_section(grader, 2, self.has_linked_CSS, pass_msg, fail_msg)

        pass_msg = "You passed the validations, great work!"
        fail_msg = ("Unfortunately you did not pass the validation. Specfically, "
                    "I found the errors below. Keep in mind that though page can still render to your browser, "
                    "there may be validation issues. If left unsolved, your code may eventually fail on different browsers. "
                    "Please ask check out the study groups or discussion forums if you need help solving these errors. "
                    "Good luck!\n{}").format(self.html_val_error_msgs)
        self._grade_web_section(grader, 3, self.html_validation, pass_msg, fail_msg)

        pass_msg = "Great work with the header tags! You know your stuff :)"
        fail_msg = ("Please make sure you have the corrent number of header tags, "
                    "which is at least 3. See this link to learn more: https://www.w3schools.com/tags/tag_header.asp")
        self._grade_web_section(grader, 4, self.has_headers, pass_msg, fail_msg)

        pass_msg = 'Great work using the div tags!'
        fail_msg = 'Please make sure you have the corrent number of div tags, which is at least 3. See this link to learn more: https://www.w3schools.com/Tags/tag_div.asp'
        self._grade_web_section(grader, 5, self.has_divs, pass_msg, fail_msg)

        pass_msg = "Nice work using the CSS Selectors! You've demonstrated some solid knowledge on these."
        fail_msg = ("Please make sure you have the corrent number of CSS Selectors, which is at least 3. "
                    "Please check out https://www.w3schools.com/cssref/css_selectors.asp for more info")
        self._grade_web_section(grader, 6, self.has_CSS_selectors, pass_msg, fail_msg)

        pass_msg = 'Nice work with the CSS selectors!'
        fail_msg = 'Please make sure you use CSS class selectors! Please see https://www.w3schools.com/cssref/css_selectors.asp if you are have trouble.'
        self._grade_web_section(grader, 7, self.has_CSS_class, pass_msg, fail_msg)

        pass_msg = "Great work using img tags, you've demonstrated some solid knowledge!"
        fail_msg = " Unfortunately you did not pass this section. Please see https://www.w3schools.com/tags/tag_img.asp if you are having difficulty with using image tags."
        self._grade_web_section(grader, 8, self.has_img, pass_msg, fail_msg)

        pass_msg = "Great work using links!"
        fail_msg = "Please see https://www.w3schools.com/html/html_links.asp if you are having difficulty with images"
        self._grade_web_section(grader, 9, self.has_link, pass_msg, fail_msg)

        logger.debug('sections 1-9 graded!') if grader.verbose else 0

    @staticmethod
    def grade_web_section_last(grader):
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
            grader.find_by_xpath_click(_grade)
            e = grader.browser.find_element(By.XPATH, _text1)
            grader.scroll_into_view(e)
            e.send_keys(msg)
            grader.find_by_xpath_click(_save1)
        except NoSuchElementException:
            # if already graded - two options...
            try:
                grader.find_by_xpath_click(_save3)
            except NoSuchElementException:
                grader.find_by_xpath_click(_save2)

    def fill_final_text_section_web(self, grader):
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
        e = grader.browser.find_element(By.XPATH, grader.final_text_xpath)
        grader.scroll_into_view(e)
        e.send_keys(msg)
        e = grader.browser.find_element(By.XPATH, grader.final_save_button_xpath)
        e.click()

    def did_pass(self):
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
