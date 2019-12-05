# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import time
from datetime import datetime

import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from values import EMAIL, PASSWORD, TWILIO_SID, TWILIO_AUTHTOKEN, TWILIO_MESSAGE_ENDPOINT, TWILIO_NUMBER, MY_NUMBER

logging.getLogger("selenium").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)


def send_whatsapp_error_message():
    message_data = {
        "To": MY_NUMBER,
        "From": TWILIO_NUMBER,
        "Body": 'The Headless Grader needs your help!',
    }
    response = requests.post(TWILIO_MESSAGE_ENDPOINT, data=message_data, auth=(TWILIO_SID, TWILIO_AUTHTOKEN))
    response_json = response.json()
    logger.info(response_json['sid'], response_json['sid'])
    return response_json


class Grader:
    def __init__(self, web_browser):
        self.browser = web_browser

        self.start = time.time()
        self.is_passing = True

        # FOR LOGIN ROUTINE
        self.email = EMAIL
        self.password = PASSWORD
        self.start_page = 'https://auth.udacity.com/sign-in?next=https%3A%2F%2Fmentor-dashboard.udacity.com%2Freviews%2Foverview'
        self.email_xpath = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div[3]/div[3]/div/form/div/div[1]/input'
        self.pass_xpath = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div[3]/div[3]/div/form/div/div[2]/input'
        self.signin_button_xpath = '/html/body/div[1]/div/div[2]/div/div/div/div[2]/div[3]/div[3]/div/form/button'
        self.queue_status_xpath1 = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div[1]/div[1]/h3'
        self.queue_status_xpath2 = '/html/body/div[1]/div/div/div[1]/div[2]/div[2]/header/div/div[2]/div/div/div[1]/div[1]/h3'
        self.queue_enter_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div/div[2]/button'
        self.queue_full_xpath = '/html/body/div[2]/div/div/div/section/div/div/div/div[2]/label'
        self.queue_now_xpath = '/html/body/div[2]/div/div/div/section/div/footer/button'
        self.queue_refresh_button_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/header/div/div[2]/div/div/div[2]/button'

        # CHECK IF GRADING ML OR WEB
        self.proj_type = None

        # FOR GETTING PENDING PROJECTS FROM THE DASHBOARD
        self.project_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/section[1]/div/ul/li/div[4]/a'
        self.time_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div[2]/section[1]/div/ul/li/div[3]/div[2]/p'

        # FOR SWITCHING TABS INSIDE GRADING
        self.code_tab_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[3]'
        self.review_tab_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[4]'
        # '/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[3]/a'

        # FOR FINAL SUBMISSION
        self.submit_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/footer/div/div/button'
        self.confirm_xpath = '/html/body/div[1]/div/div/div/form/div[2]/div/button'

        # FINAL TEXT SECTION
        self.final_text_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/ng-form/div/div/div[1]/div/div/textarea'
        self.final_save_button_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[4]/ng-form/div/div/div[2]/div/button[1]'

    def login_refresh_grade(self):
        self._login()
        self._refresh_queue()

        if self._get_project():
            self._grade_project()
        self.sleep(3)

    def _login(self):
        # a simple login routine
        self.browser.get(self.start_page)
        self.browser.find_element(By.XPATH, self.email_xpath).send_keys(self.email)
        self.browser.find_element(By.XPATH, self.pass_xpath).send_keys(self.password)
        self.browser.find_element(By.XPATH, self.signin_button_xpath).click()
        self.sleep(6)
        logger.info('Login Sucessful!')

    def _refresh_queue(self):
        # check if we're in queue or not, and enter/refresh accordingly
        try:
            queue_status = self.browser.find_element(By.XPATH, self.queue_status_xpath1).text
        except NoSuchElementException:
            queue_status = self.browser.find_element(By.XPATH, self.queue_status_xpath2).text
        if queue_status == 'Queue Off':
            self.browser.find_element(By.XPATH, self.queue_enter_xpath).click()
            self.sleep(3)
            self.browser.find_element(By.XPATH, self.queue_full_xpath).click()
            self.browser.find_element(By.XPATH, self.queue_now_xpath).click()
        else:
            self.browser.find_element(By.XPATH, self.queue_refresh_button_xpath).click()
        logger.info('Queue Refresh Sucessful!')

    def _get_project(self):
        # Open the new project, wait, then switch control to new tab
        try:
            time_remaining = self.browser.find_element(By.XPATH, self.time_xpath).text
            if 'minutes' in time_remaining:
                logger.warning(f'Only {time_remaining} minutes left.')
                return False
            time_remaining = int(time_remaining.split(' ')[0])
            if time_remaining > 7:
                logger.info('Project available but too soon to grade.')
                return False
            if time_remaining <= 5:
                logger.info('Error in grading! Manual intervention needed.')
                send_whatsapp_error_message()
                return False

            self.browser.find_element(By.XPATH, self.project_xpath).click()
            self.sleep(4)
            logger.info('Accessed new project!')
            self.browser.switch_to_window(self.browser.window_handles[1])
            self.sleep(4)
            self._check_proj_type()
            return True

        except NoSuchElementException:
            logger.info('No projects to grade')
            return False

    def _grade_project(self):
        # determine if ML or web, and grade!
        if self.proj_type == 'ml_project':
            self._grade_ml()
        elif self.proj_type == 'web_project':
            self._grade_web_project()
        self._write_logs()

    @staticmethod
    def sleep(seconds=4):
        # utility function to wait for pages to render
        time.sleep(seconds)

    def scroll_into_view(self, e):
        # scroll an element into view
        self.browser.execute_script("return arguments[0].scrollIntoView();", e)

    def find_by_xpath_click(self, xpath):
        e = self.browser.find_element(By.XPATH, xpath)
        self.scroll_into_view(e)
        e.click()

    def _check_proj_type(self):
        # check if its an ML project or not, set state.
        e = self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div[2]/div/div[1]/div/h1')
        if e.text == 'Use a Pre-trained Image Classifier to Identify Dog Breeds':
            self.proj_type = 'ml_project'
            logger.info('Grading ML Project')
        else:
            self.proj_type = 'web_project'
            logger.info('Grading Intro to Web Project')

    def get_code_tab(self):
        # in project, get the code tab where we can read code
        self.browser.find_element(By.XPATH, self.code_tab_xpath).click()

    def get_preview_tab(self):
        # in project, get the preview tab where we can grade
        self.browser.find_element(By.XPATH, self.review_tab_xpath).click()

    def submit_project(self):
        # submit the graded project!
        self.find_by_xpath_click(self.submit_xpath)
        self.sleep(2)
        self.find_by_xpath_click(self.confirm_xpath)
        logger.info('Project Submitted!')

    def _write_logs(self):
        # send logs to file
        output = f'\n{str(datetime.now())} \t' \
                 f'graded {self.proj_type} project in {"{0:.2f}".format(time.time() - self.start)}s \t' \
                 f'passing: {self.is_passing}'
        logger.info(output)
        with open('all_grades.txt', 'a') as f:
            f.write(output)

    def _grade_web_project(self):
        from web_project import WebProject
        web_proj = WebProject(grader=self)
        web_proj.grade_web_project()

    def _grade_ml(self):
        from ml_project import MLProject
        ml_proj = MLProject(grader=self)
        ml_proj.grade_ml()

# ----------------------------------------------------------------------------------------------------------------------


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
        logger.debug('Running in headless mode!')

    fp = FirefoxProfile()
    fp.set_preference("dom.webnotifications.enabled", False)
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.getcwd())
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")

    web_browser = Firefox(
        firefox_profile=fp,
        executable_path='geckodriver',
        options=options
    )
    web_browser.implicitly_wait(timeout)
    return web_browser


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--headless', default=False)
    args = parser.parse_args()

    browser = launch_browser(headless=args.headless)
    headless_grader = Grader(web_browser=browser)
    headless_grader.login_refresh_grade()
    headless_grader.browser.quit()
