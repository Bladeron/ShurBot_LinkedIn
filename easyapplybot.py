'''
You might have to install the packages corresponding to the below 
imports.
'''

import time
import random
import os
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import pyautogui
from urllib.request import urlopen

class EasyApplyBot:

    MAX_APPLICATIONS = 500

    def __init__(self, username, password, language, position, location, appliedJobIDs, filename):

        print("\nWelcome to Easy Apply Bot\n")
        dirpath = os.getcwd()
        chromepath = dirpath + '/assets/chromedriver.exe'

        self.language = language
        self.appliedJobIDs = appliedJobIDs
        self.filename = filename
        self.options = self.browser_options()
        self.browser = webdriver.Chrome(
            options=self.options, executable_path=chromepath)
        self.start_linkedin(username, password)

    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(
            "user-agent=Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393")
        options.add_argument('--no-sandbox')
        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        return options

    def start_linkedin(self, username, password):
        print("\nLogging in.....\n \nPlease wait :) \n ")
        self.browser.get(
            "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        try:
            user_field = self.browser.find_element_by_id("username")
            pw_field = self.browser.find_element_by_id("password")
            login_button = self.browser.find_element_by_css_selector(
                ".btn__primary--large")
            user_field.send_keys(username)
            user_field.send_keys(Keys.TAB)
            time.sleep(1)
            pw_field.send_keys(password)
            time.sleep(1)
            login_button.click()
        except TimeoutException:
            print("TimeoutException! Username/password field or login button not found")

    def wait_for_login(self):
        if language == "en":
            title = "Sign In to LinkedIn"
        elif language == "es":
            title = "Inicia sesión"

        time.sleep(1)

        while True:
            if self.browser.title != title:
                print("\nStarting LinkedIn bot\n")
                break
            else:
                time.sleep(1)
                print("\nPlease Login to your LinkedIn account\n")

    def fill_data(self):
        self.browser.set_window_size(0, 0)
        self.browser.set_window_position(2000, 2000)
        self.position = position
        self.location = "&location=" + location

    def start_apply(self):
        # self.wait_for_login()
        self.fill_data()
        self.applications_loop()

    def applications_loop(self):

        count_application = 0
        count_job = 0
        jobs_per_page = 0
        print("\nLooking for jobs.. Please wait..\n")

        self.browser.set_window_position(0, 0)
        self.browser.maximize_window()
        self.browser, _ = self.next_jobs_page(jobs_per_page)
        print("\nLooking for jobs.. Please wait..\n")

        while count_application < self.MAX_APPLICATIONS:
            # sleep to make sure everything loads, add random to make us look human.
            time.sleep(random.uniform(0.5, 2.3))
            self.load_page(sleep=1)

            # get job links
            links = self.browser.find_elements_by_xpath(
                '//div[@data-job-id]'
            )

            # get job ID of each job link
            IDs = []
            for link in links:
                temp = link.get_attribute("data-job-id")
                jobID = temp.split(":")[-1]
                IDs.append(int(jobID))
            IDs = set(IDs)

            # remove already applied jobs
            jobIDs = [x for x in IDs if x not in self.appliedJobIDs]

            if len(jobIDs) == 0:
                jobs_per_page = jobs_per_page + 25
                count_job = 0
                self.avoid_lock()
                self.browser, jobs_per_page = self.next_jobs_page(
                    jobs_per_page)

            # loop over IDs to apply
            for jobID in jobIDs:
                count_job += 1
                self.get_job_page(jobID)

                # get easy apply button
                button = self.get_easy_apply_button()
                if button is not False:
                    string_easy = "* Has Easy Apply Button"
                    button.click()
                    self.send_resume()
                    count_application += 1
                else:
                    string_easy = "* Doesn't have Easy Apply Button"

                position_number = str(count_job + jobs_per_page)
                print(
                    f"\nPosition {position_number}:\n {self.browser.title} \n {string_easy} \n")

                # append applied job ID to csv file
                timestamp = datetime.datetime.now()
                toWrite = [timestamp, jobID]
                with open(self.filename, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(toWrite)

                # go to new page if all jobs are done
                if count_job == len(jobIDs):
                    jobs_per_page = jobs_per_page + 25
                    count_job = 0
                    print('\n****************************************\n')
                    print('Going to next page')
                    print('\n****************************************\n')
                    self.avoid_lock()
                    self.browser, jobs_per_page = self.next_jobs_page(
                        jobs_per_page)

        self.finish_apply()

    def get_job_links(self, page):
        links = []
        for link in page.find_all('a'):
            url = link.get('href')
            if url:
                if '/jobs/view' in url:
                    links.append(url)
        return set(links)

    def get_job_page(self, jobID):
        job = 'https://www.linkedin.com/jobs/view/' + str(jobID)
        self.browser.get(job)
        self.job_page = self.load_page(sleep=0.5)
        return self.job_page

    def got_easy_apply(self, page):
        button = self.browser.find_elements_by_xpath(
            '//button[contains(@class, "jobs-apply")]/span[1]'
        )
        EasyApplyButton = button[0]
        if EasyApplyButton.text in "Easy Apply":
            return EasyApplyButton
        else:
            return False

    def get_easy_apply_button(self):
        try:
            button = self.browser.find_elements_by_xpath(
                '//button[contains(@class, "jobs-apply")]/span[1]'
            )
            EasyApplyButton = button[0]
        except:
            EasyApplyButton = False

        return EasyApplyButton

    def click_button(self, xpath):
        triggerDropDown = self.browser.find_element_by_xpath(xpath)
        time.sleep(0.5)
        triggerDropDown.click()
        time.sleep(1)

    def send_resume(self):
        submit_button = None
        follow_button = None
        time.sleep(1)
        while not submit_button:
            try:
                submit_button = self.browser.find_element_by_class_name(
                    '.artdeco-button__text')[0]
                follow_button = self.browser.find_element_by_class_name(
                    'jobs-apply-form__follow-company-label')
            except:
                print('error con el boton')
                self.start_apply()

        follow_button.click()
        time.sleep(0.3)
        submit_button.click()
        time.sleep(random.uniform(1.5, 2.5))

        print('APPLIED!!!')

    def load_page(self, sleep=1):
        scroll_page = 0
        while scroll_page < 4000:
            self.browser.execute_script(
                "window.scrollTo(0,"+str(scroll_page)+" );")
            scroll_page += 200
            time.sleep(sleep)

        if sleep != 1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep * 2)

        page = BeautifulSoup(self.browser.page_source, "html.parser")
        return page

    def avoid_lock(self):
        x, _ = pyautogui.position()
        pyautogui.moveTo(x+10, None, duration=1.0)
        pyautogui.moveTo(x, None, duration=0.5)

        time.sleep(0.5)

    def next_jobs_page(self, jobs_per_page):
        self.browser.get(
            "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=" +
            self.position + self.location + "&start="+str(jobs_per_page))

        self.avoid_lock()
        self.load_page()
        return (self.browser, jobs_per_page)

    def finish_apply(self):
        self.browser.close()


if __name__ == '__main__':
    username = 'dantexx@forocoches.com' # LinkedIn username
    password = 'vivaroto2'              # LinkedIn password
    language = 'es'                     # LinkedIn default language (en, es, pt)
    position = 'junior developer'       # job position
    # location where to apply (e.g. Barcelona)
    location = 'Madrid' #donde estan los mejores trabajos                 
    

    # print input
    '''
    print("\nInput selected:")

    print(
        "\nUsername:  " + username,
        "\nPassword:  " + password,
        "\nLanguage:  " + language,
        "\nPosition:  " + position,
        "\nLocation:  " + location
    )
    '''
    # get list of already applied jobs
    filename = 'joblist.csv'
    try:
        df = pd.read_csv(filename, header=None)
        appliedJobIDs = list(df.iloc[:, 1])
    except:
        appliedJobIDs = []

    # start bot
    bot = EasyApplyBot(username, password, language, position,
                       location, appliedJobIDs, filename)
    bot.start_apply()
