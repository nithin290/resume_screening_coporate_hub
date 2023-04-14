from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def scrapper(skill='Python Developer', location='India'):
    url = "https://in.indeed.com/jobs?q=" + skill + "&l=" + location + "&from=searchOnHP&vjk=fc431d75e835b2f0"
    base = "https://in.indeed.com"

    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = webdriver.Chrome(executable_path="D:/Selenium/chromedriver.exe", options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all(class_='resultContent')

    links = []

    for i, job in enumerate(results):
        link = job.find("a")

        # print(link)
        # print(base + link['href'])

        driver.get(base + link['href'])
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        sub_result = soup.find(class_='css-1e1cf96 eu4oa1w0')

        # print(sub_result)

        if sub_result is not None:
            apply = sub_result.find("a")
            links.append(apply['href'])
        else:
            links.append(base + link['href'])

        print(f'link {i+1}. {links[i]}')

    return links


def main():
    scrapper()


if __name__ == '__main__':
    main()
