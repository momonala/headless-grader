from grader import launch_browser, Grader
import schedule
import argparse
import time
import traceback
import sys
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--headless', default=False)
args = parser.parse_args()

if args.headless:
    raise NotImplementedError('Headless mode not working - copying clipboard with cntrl+C in headless unimplemented')


def grade():
    # start a session to grade a project!
    try:
        browser = launch_browser(headless=args.headless)

        headless_grader = Grader(browser, verbose=False)
        headless_grader.login()
        headless_grader.refresh_queue()

        if headless_grader.get_project():
            headless_grader.grade_project(log=True)

        headless_grader.SLEEP(2)
        headless_grader.browser.quit()

    # if it fails, log and continue onward
    except Exception:
        err_msg = '******* FAILED {} ************ '.format(format(str(datetime.now())))
        print(err_msg)

        with open('grades.txt', 'a') as f:
            f.write('******************************************************\n')
            f.write(err_msg + '\n')
            f.write(traceback.format_exc())

        headless_grader.browser.quit()

grade()
schedule.every(30).minutes.do(grade)

while True:
    schedule.run_pending()
    time.sleep(1)
