import scrapy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..items import JobItem
import json
from urllib.parse import urlparse, urlencode
from ..utils.logger import debug, info, warn, error
from ..utils.constants import *
from pymongo import MongoClient
from ..settings import *
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

load_dotenv()

class TopcvScraperSpider(scrapy.Spider):
    name = 'topcv-scraper'

    def __init__(self, *args, **kwargs):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client["Grab-Data"]
        self.page = 0  # Start page
        # Set up Selenium Chrome driver
        self.options = Options()
        self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(options=self.options)

    def close(self, reason):
        self.driver.quit()
        super().close(reason)

    def load_config(self, file_name):
        with open(file_name) as f:
            return json.load(f)

    def load_query(self):
        query_collection = self.db["search_queries"]
        return query_collection.find()

    def build_search_url(self, query):
        if query is None:
            return JOBS_SEARCH_URL
        url = JOBS_SEARCH_URL
        params = {}

        if query.get('keywords'):
            url += "-" + query['keywords'].replace(' ', '-')

        if query.get('location'):
            url += "-tai-" + query['location'].lower().replace(' ', '-') + "-l" + cities_reverse[query['location']]

        if query.get('relevance'):
            params['sort'] = query['relevance']
            debug(f'[{query.get("keywords")}][{query.get("location")}]', 'Applied relevance filter', query['relevance'])

        if query.get('type'):
            url += "/t" + types_reverse[query['type']]

        if query.get('industry'):
            params['company_fields'] = industry_reverse[query['industry']]
            debug(f'[{query.get("keywords")}][{query.get("location")}]', 'Applied industry filters', query['industry'])

        params['page'] = str(self.page)
        parsed = urlparse(url)
        self.page += 1
        parsed = parsed._replace(query=urlencode(params))
        return parsed.geturl()

    def start_requests(self):
        config = self.load_config('config.json')
        for query in config['search_queries']:
            self.page = 0
            for _ in range(config['num_pages']):
                url = self.build_search_url(query)
                yield scrapy.Request(url, callback=self.parse, headers=config['headers'], meta={'config': config, 'query': query})

    def parse(self, response):
        config = response.meta['config']
        query = response.meta['query']

        driver = self.driver
        driver.get(response.url)

        try:
            cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.job-item-search-result.bg-highlight.job-ta'))
            )
            print(f'Found {len(cards)} jobs')
            for card in cards:
                try:
                    job_item = self.extract_job_details(card, query)
                    print(job_item)
                    yield job_item
                except Exception as e:
                    print(f"An error occurred: {e}")
        finally:
            # No need to quit the driver here, it will be handled by the spider closing process
            pass

    def extract_job_details(self, card, query):
        title, company, company_link, company_location, location, job_url = "Not Available", "Not Available", "Not Available", "Not Available", "Not Available", "Not Available"
        description = ""

        title_element = self.find_element(card, 'h3.title > a > span')
        if title_element:
            title = title_element.text.strip()

        company_element = self.find_element(card, 'a.company')
        if company_element:
            company = company_element.text.strip()
            company_link = company_element.get_attribute('href')

        location_element = self.find_element(card, 'div.info > div.label-content > label.address')
        if location_element:
            html_string = location_element.get_attribute("data-original-title")
            soup = BeautifulSoup(html_string, 'html.parser')
            company_location_element = soup.find('p')
            if company_location_element:
                company_location = company_location_element.text.strip()
            location = location_element.text.strip()

        job_url_element = self.find_element(card, 'div.title-block > div > h3.title > a')
        if job_url_element:
            job_url = job_url_element.get_attribute('href')

        # Create job item
        job_item = {
            'title': title,
            'company': company,
            'company_link': company_link,
            'company_location': company_location,
            'location': location,
            'job_url': job_url,
            'query': query,
            'description': description
        }

        # Get the job description asynchronously
        if job_url:
            try:
                new_driver = webdriver.Chrome(options=self.options)
                new_driver.get(job_url)
                new_driver.implicitly_wait(1.4)
                div = new_driver.find_element(By.CSS_SELECTOR, 'div.job-detail__box--left')
                if div:
                    text = div.text.strip().replace('\n\n', '').replace('::marker', '-').replace('-\n', '- ')
                    job_item['description'] = text
            finally:
                new_driver.quit()

        return job_item

    def find_element(self, element, selector):
        try:
            return element.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None
