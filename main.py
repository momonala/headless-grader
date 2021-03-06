#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import time
import traceback
from datetime import datetime

import schedule

from grader import launch_browser, Grader

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--headless', default=False)
args = parser.parse_args()

if args.headless:
    logger.info('Running in Headless mode!')


def grade():
    # start a session to grade a project!
    browser = launch_browser(headless=args.headless, timeout=8)
    headless_grader = Grader(browser)
    try:
        headless_grader.login_refresh_grade()

    except Exception:
        err_msg = '***** FAILED {} ***** '.format(format(str(datetime.now())))
        logger.error(err_msg, exc_info=True)
        with open('logs.txt', 'a') as f:
            f.write('******************************************************\n')
            f.write(err_msg + '\n')
            f.write(traceback.format_exc())
    headless_grader.browser.quit()
grade()

schedule.every(60).minutes.do(grade)

while True:
    schedule.run_pending()
    time.sleep(1)
