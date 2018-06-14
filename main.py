from grader import launch_browser, Grader
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--phantom', default=False)
args = parser.parse_args()

# start a session to grade a project!
browser = launch_browser(phantom=args.phantom)

headless_grader = Grader(browser)
headless_grader.login()
headless_grader.refresh_queue()

if headless_grader.get_project():
    headless_grader.grade_project()

headless_grader.SLEEP(3)
headless_grader.browser.quit()
