from grader import launch_browser, Grader
import schedule
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--headless', default=False)
args = parser.parse_args()

if args.headless:
    raise NotImplementedError('Headless mode not working - cntrl+C unimplemented')


def grade():
    # start a session to grade a project!
    browser = launch_browser(headless=args.headless)

    headless_grader = Grader(browser)
    headless_grader.login()
    headless_grader.refresh_queue()

    if headless_grader.get_project():
        headless_grader.grade_project(log=True)

    headless_grader.SLEEP(2)
    headless_grader.browser.quit()


schedule.every(1).minutes.do(grade)

while True:
    schedule.run_pending()
    time.sleep(1)
