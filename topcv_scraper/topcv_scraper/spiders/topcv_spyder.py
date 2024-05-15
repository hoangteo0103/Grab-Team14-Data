import scrapy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..items import JobItem
import json
from urllib.parse import urlparse, urlencode
from ..utils.logger import debug, info, warn, error
from ..filters.filters import *
from pymongo import MongoClient
from ..settings import *
from ..utils.constants import *
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

load_dotenv()

class TopcvScraperSpider(scrapy.Spider):
    name = 'topcv-scraper'

    def __init__(self, *args, **kwargs):
        self.queries = kwargs.get('queries')
        self.config = kwargs.get('config')

        self.page = 0  # Start page
        # Set up Selenium Chrome driver
        self.options = Options()
        self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(options=self.options)

    def close(self, reason):
        self.driver.quit()
        super().close(reason)

    def build_search_url(self, query):
        if query is None:
            return JOBS_SEARCH_URL
        url = JOBS_SEARCH_URL
        params = {}

        if query.get('keywords'):
            url += "-" + query['keywords'].replace(' ', '-')

        if query.get('location'):
            url += "-tai-" + query['location'].lower().replace(' ', '-') + "-l" + CityFilter.getValueFromKey(query['location'])
        if query.get('relevance'):
            params['sort'] = query['relevance']
            debug(f'[{query.get("keywords")}][{query.get("location")}]', 'Applied relevance filter', query['relevance'])

        if query.get('type'):
            url += "/t" + JobTypeFilter.getValueFromKey(query['type'])

        if query.get('industry'):
            params['company_fields'] = IndustryFilter.getValueFromKey(query['industry'][0])
            debug(f'[{query.get("keywords")}][{query.get("location")}]', 'Applied industry filters', query['industry'])

        params['page'] = str(self.page)
        parsed = urlparse(url)
        self.page += 1
        parsed = parsed._replace(query=urlencode(params))
        return parsed.geturl()

    def start_requests(self):
        for query in self.queries:
            industries = query.get('industry', [])

            query_industries = IndustryFilter.getValueFromKey(industries[0]) if industries else None
            query_industries = query_industries.split('.') if query_industries else None
            self.page = 0
            for industry in query_industries:
                for _ in range(self.config['num_pages']):
                    new_query = query.copy()

                    new_query['industry'] = industry
                    url = self.build_search_url(query)
                    yield scrapy.Request(url, callback=self.parse, headers=self.config['headers'], meta={'config': self.config, 'query': new_query, 'orginal_query': query})

    def parse(self, response):
        config = response.meta['config']
        query = response.meta['query']
        original_query = response.meta['orginal_query']

        driver = self.driver
        driver.get(response.url)

        try:
            cards = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.job-item-search-result.bg-highlight.job-ta'))
            )
            print(f'Found {len(cards)} jobs')
            for card in cards:
                try:
                    job_item = self.extract_job_details(card, query, original_query)
                    print(job_item)
                    yield job_item
                except Exception as e:
                    print(f"An error occurred: {e}")
        finally:
            # No need to quit the driver here, it will be handled by the spider closing process
            pass

    def extract_job_details(self, card, query, original_query):
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
            'original_query': original_query
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
                    job_item['job_description'] = text
            finally:
                new_driver.quit()

        return job_item

    def find_element(self, element, selector):
        try:
            return element.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None
