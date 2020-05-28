import csv
import os
import re
import time
from os.path import isfile
from selenium import webdriver
from tldextract import tldextract

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"
}


def read_input_from_csv(path):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]


def get_files_to_parse():
    files = os.listdir('files')
    files = [f'files/{file}' for file in files if isfile(f'files/{file}')]
    return files


def get_driver(headless=True, proxies=None):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", HEADERS["User-Agent"])

    options = webdriver.FirefoxOptions()
    if headless:
        options.headless = True

    if proxies is not None:
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxies["ip"])
        profile.set_preference("network.proxy.http_port", int(proxies["port"]))
        profile.set_preference("network.proxy.ssl", proxies["ip"])
        profile.set_preference("network.proxy.ssl_port", int(proxies["port"]))

    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver.implicitly_wait(3)

    return driver


def write_report(data: list):
    with open('report.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)


class DetailPageScraper:
    def __init__(self, headless=False, *args, **kwargs):
        self.driver = None
        self.headless = headless
        super().__init__(*args, **kwargs)

    def __enter__(self):
        """ Initiate browser. """
        self.driver = get_driver(headless=self.headless)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def make_request(self, url):
        self.driver.get(url)

        title = self.driver.title
        title = title.replace(' ', '_')

        try:
            email = self.driver.find_element_by_xpath('//td[@itemprop="email"]').text
            if 'click to get email address' in email.lower():
                self.driver.find_element_by_xpath('//td[@itemprop="email"]/span').click()
                time.sleep(2)
        except:
            pass

        html = self.driver.page_source
        with open(f'files/{title}.html', 'w') as file:
            file.write(html)


class DetailPageParser:
    def extract(self, html):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'lxml')

        profile = soup.find(attrs={'class': 'enf-company-profile'})

        if not profile:
            print(f'Company {soup.title.text} has no contact info')
            return {}

        company_name = profile.find('h1').text.strip()
        try:
            address = profile.find(attrs={'itemprop': 'address'}).text.strip()
        except:
            address = None

        try:
            telephone = profile.find(attrs={'itemprop': 'telephone'}).text.strip()
        except:
            telephone = None

        try:
            email = profile.find(attrs={'itemprop': 'email'}).text.strip()
        except:
            email = None

        try:
            url = profile.find(attrs={'itemprop': 'url'}).text.strip()
        except:
            url = None

        try:
            breadcrumps = soup.find(attrs={'class': 'enf-breadcrumb'})
            country = breadcrumps.find_all('li')[1].text.strip()
        except:
            country = None

        try:
            last_update = soup.find(text=re.compile('Last Update', flags=re.I))
            last_update = last_update.parent.parent.find(attrs={'class': 'enf-section-body-content'}).text.strip()
            last_update = last_update.split('\n')[0]
        except:
            last_update = None

        try:
            language = soup.find(text=re.compile('Languages Spoken', flags=re.I))
            language = language.parent.parent.find(attrs={'class': 'enf-section-body-content'}).text.strip()
        except Exception as e:
            language = None

        try:
            suppliers = soup.find(text=re.compile('Panel Suppliers', flags=re.I))
            suppliers = suppliers.parent.parent.find(attrs={'class': 'enf-section-body-content'}).text.strip()
        except Exception as e:
            suppliers = None

        try:
            panel = soup.find(text=re.compile('Panel', flags=re.I))
            panel = panel.parent.parent.find(attrs={'class': 'enf-section-body-content'}).text.strip()
        except:
            panel = None

        try:
            service_coverage = soup.find(text=re.compile('Service Coverage', flags=re.I))
            service_coverage = service_coverage.parent.parent.find(attrs={'class': 'enf-section-body-content'}).text.strip()
        except:
            service_coverage = None

        try:
            operating_area = soup.find(text=re.compile('Operating Area', flags=re.I))
            operating_area = operating_area.parent.parent.find(attrs={'class': 'enf-section-body-content'}).text.strip()
        except:
            operating_area = None

        if url:
            domain = tldextract.extract(url).registered_domain
        else:
            domain = None

        return {
            'Company Name': company_name,
            'Address': address,
            'Country': country,
            'Telephone': telephone,
            'Email': email,
            'Website': url,
            'Domain': domain,
            'Panel': panel,
            'Service Coverage': service_coverage,
            'Languages Spoken': language,
            'Last Update': last_update,
            'Panel Suppliers': suppliers,
            'Operating Area': operating_area,
        }


