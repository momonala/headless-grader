# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from itertools import permutations

from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLProject:
    def __init__(self):
        self.perms = permutations(range(1, 7), 4)
        self.known_xpaths = []

    def grade_ml_section(self, grader, button_x, text_x, save_x, msg, save_x2_li=list(), section=None):
        """ Grade an ML section. If already graded, iterate through a list of high probablity save xpaths.
        If that fails, iterate throuhg every possible permutation, given our knowledge about how the
        paths are formatted (brute force). """
        try:
            grader.find_by_xpath_click(button_x)
            e = grader.browser.find_element(By.XPATH, text_x)
            grader.scroll_into_view(e)
            e.send_keys(msg)
            grader.find_by_xpath_click(save_x)
            return

        # if we're here, then this section has likely already been graded
        except NoSuchElementException:
            for x in save_x2_li:
                try:
                    grader.find_by_xpath_click(x)
                    return
                except NoSuchElementException:
                    pass
            if section not in [1, 13]:
                logger.debug(f'Predefined XPATHS failed for section {section}. Attemping loop.')
                p = self._grade_arbitrary_ml_section(grader)
                logger.debug(f'section:{section} - {p} worked!')
            else:
                logger.debug(f'Predefined XPATHS for section {section} failed.')

    @staticmethod
    def _get_arbitrary_xpath(w, x, y, z):
        # Generate an xpath for an arbitrary section save.
        return f'/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[{w}]/div/div/div[{x}]/div[{y}]/div/div/ng-form/div[{z}]/div[2]/div/button[1]'

    def _grade_arbitrary_ml_section(self, grader):
        # Grade an arbitrary section or throw an error if failure.
        for p in self.perms:
            xpath = self._get_arbitrary_xpath(*p)
            if xpath not in self.known_xpaths:
                try:
                    grader.find_by_xpath_click(xpath)
                    return p
                except NoSuchElementException:
                    pass
        raise InvalidSelectorException('New or unknown xpath for this section!')

    def grade_all_ml_sections(self, grader):
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
        x2 = [self._get_arbitrary_xpath(2, 2, 1, 2), self._get_arbitrary_xpath(2, 2, 1, 3),
              self._get_arbitrary_xpath(2, 2, 1, 4)]
        x3 = [self._get_arbitrary_xpath(2, 2, 2, 2), self._get_arbitrary_xpath(2, 2, 2, 3)]
        x4 = [self._get_arbitrary_xpath(2, 2, 3, 2), self._get_arbitrary_xpath(2, 2, 3, 3)]
        x5 = [self._get_arbitrary_xpath(3, 2, 1, 2), self._get_arbitrary_xpath(3, 2, 1, 3),
              self._get_arbitrary_xpath(3, 2, 1, 4)]
        x6 = [self._get_arbitrary_xpath(3, 2, 2, 3), self._get_arbitrary_xpath(3, 2, 3, 2),
              self._get_arbitrary_xpath(3, 2, 2, 2), x6_save1]
        x7 = [self._get_arbitrary_xpath(3, 2, 3, 2), self._get_arbitrary_xpath(3, 2, 3, 3),
              self._get_arbitrary_xpath(4, 2, 1, 2), self._get_arbitrary_xpath(4, 2, 1, 3)]
        x8 = [self._get_arbitrary_xpath(4, 2, 1, 3), self._get_arbitrary_xpath(4, 2, 2, 2),
              self._get_arbitrary_xpath(4, 2, 3, 2), self._get_arbitrary_xpath(4, 2, 2, 3)]
        x9 = [self._get_arbitrary_xpath(4, 2, 2, 2), self._get_arbitrary_xpath(5, 2, 1, 2),
              self._get_arbitrary_xpath(4, 2, 3, 3)]
        x10 = [self._get_arbitrary_xpath(4, 2, 3, 4), self._get_arbitrary_xpath(4, 2, 3, 2),
               self._get_arbitrary_xpath(4, 2, 3, 3), self._get_arbitrary_xpath(5, 2, 2, 2)]
        x11 = [self._get_arbitrary_xpath(5, 2, 1, 2), self._get_arbitrary_xpath(5, 2, 1, 3),
               self._get_arbitrary_xpath(5, 2, 1, 4), self._get_arbitrary_xpath(4, 2, 2, 3)]
        x12 = [self._get_arbitrary_xpath(5, 2, 2, 4), self._get_arbitrary_xpath(5, 2, 2, 2),
               self._get_arbitrary_xpath(5, 2, 2, 3), self._get_arbitrary_xpath(6, 2, 1, 3)]
        x13 = [x13_save1, x13_save2]
        self.known_xpaths = [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x12]

        self.grade_ml_section(grader, _button_x1, _text_x1, _save_x1, msg_1, x1, 1)
        self.grade_ml_section(grader, _button_x2, _text_x2, _save_x2, msg_2, x2, 2)
        self.grade_ml_section(grader, _button_x3, _text_x3, _save_x3, msg_3, x3, 3)
        self.grade_ml_section(grader, _button_x4, _text_x4, _save_x4, msg_4, x4, 4)
        self.grade_ml_section(grader, _button_x5, _text_x5, _save_x5, msg_5, x5, 5)
        self.grade_ml_section(grader, _button_x6, _text_x6, _save_x6, msg_6, x6, 6)
        self.grade_ml_section(grader, _button_x7, _text_x7, _save_x7, msg_7, x7, 7)
        self.grade_ml_section(grader, _button_x8, _text_x8, _save_x8, msg_8, x8, 8)
        self.grade_ml_section(grader, _button_x9, _text_x9, _save_x9, msg_9, x9, 9)
        self.grade_ml_section(grader, _button_x10, _text_x10, _save_x10, msg_10, x10, 10)
        self.grade_ml_section(grader, _button_x11, _text_x11, _save_x11, msg_11, x11, 11)
        self.grade_ml_section(grader, _button_x12, _text_x12, _save_x12, msg_12, x12, 12)
        self.grade_ml_section(grader, _button_x13, _text_x13, _save_x13, msg_13, x13, 13)

    @staticmethod
    def fill_final_section_ml(grader):
        # senf the final message about the whole project to the student.
        msg = "Awesome work on this project! You've demonstrated a solid understanding of using ML classifiers within Python. Onward to the next project!"
        final_text_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[8]/ng-form/div/div/div[1]/div/div/textarea'
        final_save_button_xpath = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div/section[5]/div[2]/div/div[8]/ng-form/div/div/div[2]/div/button[1]'

        e = grader.browser.find_element(By.XPATH, final_text_xpath)
        grader.scroll_into_view(e)
        e.send_keys(msg)
        grader.browser.find_element(By.XPATH, final_save_button_xpath).click()
