import scrapy
from urllib.parse import quote
from datetime import datetime
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from ..items import JobItem
import json
from urllib.parse import urlparse, urlencode
from ..utils.constants import *
from ..utils.logger import debug
from ..settings import *
import os
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from scrapy_splash import SplashRequest


load_dotenv()

load_page_script="""
        function main(splash)
            splash:set_user_agent(splash.args.ua)
            assert(splash:go(splash.args.url))
            splash:wait(5) -- Wait for 5 seconds

            repeat
                splash:wait(0.5)
            until splash:select('div.ivm-image-view-model') ~= nil 

            return {html=splash:html()}
        end
"""


class LinkedInScraperSpider(scrapy.Spider):
    name = 'linkedin-scraper'
    custom_settings = {
    'SPLASH_URL': 'http://localhost:8060',
    # if installed Docker Toolbox: 
    #  'SPLASH_URL': 'http://192.168.99.100:8050',
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy_splash.SplashCookiesMiddleware': 723,
        'scrapy_splash.SplashMiddleware': 725,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        'linkedin_scraper.middlewares.TooManyRequestsRetryMiddleware': 543,
    },
    'SPIDER_MIDDLEWARES': {
        'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    },
    'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    }

    def __init__(self, *args, **kwargs):
     self.queries = kwargs.get('queries')
     self.config = kwargs.get('config')
     self.start = 0 # Start page
     self.stop = False
     
        
    def build_search_url(self, query):
        if query is None:
            return JOBS_SEARCH_URL
        tag = f'[{query.get('keywords')}][{query.get('location')}]'
        parsed = urlparse(JOBS_SEARCH_URL)
        params = {}

        if query.get('keywords') is not None and len(query['keywords']) > 0:
            params['keywords'] = query['keywords']

        if query.get('location') is not None and len(query['location']) > 0:
            params['location'] = query['location']


        if query.get('time') is not None and len(query['time']) > 0:
            params['f_TPR'] = query['time']
            debug(tag, 'Applied time filter', query['time'])
        
        if query.get('relevance') is not None and len(query['relevance']) > 0:
            params['sortBy'] = query['relevance']
            debug(tag, 'Applied relevance filter', query['relevance'])
          
        if query.get('type') is not None and len(query['type']) > 0:
            filters = ','.join(e for e in query['type'])
            params['f_JT'] = filters
            debug(tag, 'Applied type filters', query['type'])
        
        if query.get('experience') is not None and len(query['experience']) > 0:
            filters = ','.join(e for e in query['experience'])
            params['f_E'] = filters
            debug(tag, 'Applied experience filters', query['experience'])
        

        if query.get('industry') is not None and len(query['industry']) > 0:
            filters = ','.join(e for e in query['industry'])
            params['f_I'] = filters
            debug(tag, 'Applied industry filters', query['industry'])
        
        
        params['start'] = str(self.start)

        self.start += 25

        parsed = parsed._replace(query=urlencode(params))
        return parsed.geturl()
    def load_config(self, path):
        with open(path) as f:
            return json.load(f)
    
    def start_requests(self):
        for query in self.queries:
            self.start = 0
            for i in range(self.config['num_pages']):
                if self.stop:
                    break
                url = self.build_search_url(query)
                yield SplashRequest(url, self.parse, meta={'config': self.config, 'query': query},args={'wait': 0.5})
    
    def parse(self, response):
        config = response.meta['config']
        query = response.meta['query']


        if response.status == 400:
            self.stop = True
            return
        joblist = []
        # Extracting job cards
        cards = response.css('div.base-search-card__info')
        for card in cards:
            if card is None:
                continue
            # Extracting job details using Scrapy selectors
            title = card.css('h3::text').get(default='not-found').strip()
            company = card.css('a.hidden-nested-link::text').get(default='not-found').strip()
            companyLink = card.css('h4 a::attr(href)').get(default='not-found')
            companyLocation = card.css('.job-search-card__location::text').get(default='not-found').strip()
            location = card.css('span.job-search-card__location::text').get(default='not-found').strip()
            entity_urn = card.xpath('../@data-entity-urn').get(default='not-found')
            job_posting_id = entity_urn.split(':')[-1]
            jobLink = f'https://www.linkedin.com/jobs/view/{job_posting_id}/'
            date_tag = card.css('time.job-search-card__listdate').attrib.get('datetime', '')
            date_tag_new = card.css('time.job-search-card__listdate--new').attrib.get('datetime', '')

            

            date = date_tag if date_tag else date_tag_new

            # Create a job item without description
            job_item = {
                'title': title,
                'company': company,
                'companyLink': companyLink,
                'companyLocation': companyLocation,
                'location': location,
                'date': date,
                'jobLink': jobLink,
                'query': query,
            }


            splash_args = {
            'render_all': 1,
            'ua': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            'lua_source': load_page_script
            }
            yield SplashRequest(jobLink, self.parse_description,endpoint='execute', magic_response=True, headers=config['headers'], meta={'job_item': job_item, 'config': config},args=splash_args)

    def parse_description(self, response):
        config = response.meta['config']
        job_item = response.meta['job_item']

        description_div = response.css('div.description__text.description__text--rich')
        companyImageUrl = response.css("div.details.mx-details-container-padding > div.sub-nav-cta__content > img").attrib.get('src', '')
        workingMode = response.css("span.ui-label.ui-label--accent-3.text-body-small > span").get(default='not-found').strip()


        print("companyImageUrl", companyImageUrl)
        job_item['companyImageUrl'] = companyImageUrl
        job_item['workingMode'] = workingMode
        with open('response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        if description_div:
            # Remove unwanted elements
            for element in description_div.css('span, a'):
                element.extract()

            # Get the cleaned text
            description = '\n'.join(description_div.xpath('.//text()').extract()).strip()
            description = description.replace('\n\n', '')
            description = description.replace('::marker', '-')
            description = description.replace('-\n', '- ')
            description = description.replace('Show less', '').replace('Show more', '')
        else:
            description = "Could not find Job Description"
        job_item['description'] = description
        yield job_item

    def remove_irrelevant_jobs(self, joblist, config):
        new_joblist = [job for job in joblist if not any(word.lower() in job['description'].lower() for word in config['desc_words'])]   
        new_joblist = [job for job in new_joblist if not any(word.lower() in job['title'].lower() for word in config['title_exclude'])] if len(config['title_exclude']) > 0 else new_joblist
        new_joblist = [job for job in new_joblist if any(word.lower() in job['title'].lower() for word in config['title_include'])] if len(config['title_include']) > 0 else new_joblist
        new_joblist = [job for job in new_joblist if self.safe_detect(job['description']) in config['languages']] if len(config['languages']) > 0 else new_joblist
        new_joblist = [job for job in new_joblist if not any(word.lower() in job['company'].lower() for word in config['company_exclude'])] if len(config['company_exclude']) > 0 else new_joblist
        return new_joblist

    def safe_detect(self, text):
        try:
            return detect(text)
        except LangDetectException:
            return 'en'
