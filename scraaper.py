import pandas as pd
import re

from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from IPython.core.display import clear_output
from random import randint
from requests import get
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from time import time

start_time = time()

from warnings import warn

# url = "https://www.linkedin.com/jobs/search?keywords=Software&location=India&f_TP=1%2C2"
url = "https://www.linkedin.com/jobs/search/?keywords=Software&location=India&f_TP=1&redirect=false&position=1&pageNum=0"
no_of_jobs = 1000

driver = webdriver.Chrome(executable_path=r'D:\\projects\\Data\\proj\\linkedin\\chromedriver_win32\\chromedriver')
driver.get(url)
sleep(3)
action = ActionChains(driver)

SCROLL_PAUSE_TIME = 2

last_height = driver.execute_script("return document.body.scrollHeight")

i = 2
while i <= (no_of_jobs / 25):
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)
    try:
        temp = driver.find_element_by_xpath(
            "/html/body/main/div/section/button"
        ).click()
    except:
        print("not found")

    i = i + 1
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    last_height = new_height

# i = 2
# while i <= (no_of_jobs/25):
#     driver.find_element_by_xpath('/html/body/main/div/section/button').click()
#     i = i + 1
#     sleep(5)

pageSource = driver.page_source
lxml_soup = BeautifulSoup(pageSource, "lxml")

# searching for all job containers
job_container = lxml_soup.find("ul", class_="jobs-search__results-list")

print("You are scraping information about {} jobs.".format(len(job_container)))
pattern = re.compile("[2-9]{1,2}.{0,10}[Yy][Ee]?[Aa]?[Rr][sS]?")

job_id = []
post_title = []
company_name = []
post_date = []
job_location = []
job_desc = []
level = []
emp_type = []
url = []
removeIndexes = []
# for loop for job title, company, id, location and date posted
for job in job_container:

    # job title
    job_titles = job.find("span", class_="screen-reader-text").text
    post_title.append(job_titles)

    # linkedin job id
    job_ids = job.find("a", href=True)["href"]
    job_ids = re.findall(r"(?!-)([0-9]*)(?=\?)", job_ids)[0]
    job_id.append(job_ids)

    # company name
    company_names = job.select_one("img")["alt"]
    company_name.append(company_names)

    # job location
    job_locations = job.find("span", class_="job-result-card__location").text
    job_location.append(job_locations)

    # posting date
    post_dates = job.select_one("time")["datetime"]
    post_date.append(post_dates)

# for loop for job description and criterias
for x in range(1, len(job_id) + 1):
    try:
        # clicking on different job containers to view information about the job
        job_xpath = "/html/body/main/div/section/ul/li[{}]/img".format(x)
        driver.find_element_by_xpath(job_xpath).click()
        sleep(3)

        # job description
        jobdesc_xpath = "/html/body/main/section/div[2]/section[2]"
        sleep(1)
        btn = driver.find_element_by_class_name("show-more-less-html__button--more")
        if btn is not None:
            btn.click()
        sleep(1)
        job_descs = driver.find_element_by_class_name("description__text--rich").text
        if re.search(pattern, job_descs):
            removeIndexes.append(x - 1)
            continue
        url.append(driver.current_url)
        job_desc.append(job_descs)

        # job criteria container below the description
        job_criteria_container = lxml_soup.find("ul", class_="job-criteria__list")
        all_job_criterias = job_criteria_container.find_all(
            "span", class_="job-criteria__text job-criteria__text--criteria"
        )

        # Seniority level
        seniority_xpath = "/html/body/main/section/div[2]/section[2]/ul/li[1]"
        seniority = driver.find_element_by_xpath(seniority_xpath).text.splitlines(0)[1]
        level.append(seniority)

        # Employment type
        type_xpath = "/html/body/main/section/div[2]/section[2]/ul/li[2]"
        employment_type = driver.find_element_by_xpath(type_xpath).text.splitlines(0)[1]
        emp_type.append(employment_type)
    except Exception as e:
        print(e)
        removeIndexes.append(x - 1)

    x = x + 1
# to check if we have all information
for index in sorted(removeIndexes, reverse=True):
    del job_id[index]
    del post_date[index]
    del company_name[index]
    del post_title[index]
    del job_location[index]


print(len(job_id))
print(len(post_date))
print(len(company_name))
print(len(post_title))
print(len(job_location))
print(len(job_desc))
print(len(level))
print(len(emp_type))


job_data = pd.DataFrame(
    {
        "Job ID": job_id,
        "Date": post_date,
        "Company Name": company_name,
        "Post": post_title,
        "Location": job_location,
        "Description": job_desc,
        "url": url,
        "Level": level,
        "Type": emp_type,
    }
)

# cleaning description column
job_data["Description"] = job_data["Description"].str.replace("\n", " ")

print(job_data.info())
job_data.head()
job_data.to_csv("LinkedIn Job Data.csv" + str(start_time), index=0, encoding="utf-8")

