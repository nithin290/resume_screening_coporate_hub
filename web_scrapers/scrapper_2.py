from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import bs4 as bs
from bs4 import BeautifulSoup

import pandas as pd

main_df = pd.read_csv('../assets/links_new.csv', index_col=0)
if main_df.size != 0:
    main_df = pd.DataFrame(
        columns=["Job Title", "Company Job Title", "Company Link", "Company Name", "Company Location"])


def scrapper(skill='Python Developer', location='India'):
    global main_df

    df = pd.DataFrame(columns=["Job Title", "Company Job Title", "Company Link", "Company Name", "Company Location"])

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    # driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)

    DRIVER_PATH = 'D:/Selenium/chromedriver.exe'
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    url = "https://in.indeed.com/jobs?q=" + skill + "&l=" + location + "&from=searchOnHP&vjk=fc431d75e835b2f0"
    base = "https://in.indeed.com"

    options = Options()
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    soup = bs.BeautifulSoup(driver.page_source, 'html.parser')
    for ele in soup.find_all(class_="css-1m4cuuf e37uo190"):
        ele = ele.parent()
        job = ele[0].find(class_="jcs-JobTitle css-jspxzf eu4oa1w0")
        s1 = base + job["href"]
        cn = ele[6].find(class_="turnstileLink companyOverviewLink")
        if cn is not None:
            cn = cn.text
        lc = ele[4].find(class_="companyLocation")
        if lc is not None:
            lc = lc.text

        df.loc[len(df.index)] = [skill, job.text, s1, cn, lc]

    print(df.head())
    main_df = pd.concat([main_df, df], ignore_index=True)
    main_df.to_csv('../assets/links_new.csv', index=True)


def main():
    global df

    categories = ["Data Science", "HR", "Advocate", "Arts", "Web Designing", "Mechanical Engineer", "Sales",
                  "Health and fitness", "Civil Engineer", "Java Developer", "Business Analyst", "SAP Developer",
                  "Automation Testing", "Electrical Engineering", "Operations Manager", "Python Developer",
                  "DevOps Engineer", "Network Security Engineer", "PMO", "Database", "Hadoop", "ETL Developer",
                  "DotNet Developer", "Blockchain", "Testing"]

    for category in categories:
        print(category)
        scrapper(skill=category)
        links = []


if __name__ == '__main__':
    main()
