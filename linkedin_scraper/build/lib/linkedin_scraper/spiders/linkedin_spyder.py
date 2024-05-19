import scrapy
from urllib.parse import quote
from datetime import datetime
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from ..items import JobItem
import json
from urllib.parse import urlparse, urlencode
from ..utils.logger import debug, info, warn, error
from ..utils.constants import *
from pymongo import MongoClient
from ..settings import *
import os
from dotenv import load_dotenv

load_dotenv()


class LinkedInScraperSpider(scrapy.Spider):
    name = 'linkedin-scraper'

    def __init__(self, *args, **kwargs):
     self.client = MongoClient(os.getenv('MONGODB_URI'))
     self.db = self.client["Grab-Data"]
     self.start = 0 # Start page

    def load_config(self, file_name):
        # Load the config file
        with open(file_name) as f:
            return json.load(f)
    
    def load_query(self):
        query_collection = self.db["search_queries"]
        queries = query_collection.find()
        return queries
        
    def build_search_url(self, query):
        if query is None:
            return JOBS_SEARCH_URL
        tag = f'[{query.get('keywords')}][{query.get('location')}]'
        parsed = urlparse(JOBS_SEARCH_URL)
        params = {}

        if query.get('keywords') is not None:
            params['keywords'] = query['keywords']

        if query.get('location') is not None:
            params['location'] = query['location']


        if query.get('time') is not None:
            params['f_TPR'] = query['time']
            debug(tag, 'Applied time filter', query['time'])
        
        if query.get('relevance') is not None:
            params['sortBy'] = query['relevance']
            debug(tag, 'Applied relevance filter', query['relevance'])
          
        if query.get('type') is not None:
            filters = ','.join(e for e in query['type'])
            params['f_JT'] = filters
            debug(tag, 'Applied type filters', query['type'])
        
        if query.get('experience') is not None:
            filters = ','.join(e for e in query['experience'])
            params['f_E'] = filters
            debug(tag, 'Applied experience filters', query['experience'])
        

        if query.get('industry') is not None:
            filters = ','.join(e for e in query['industry'])
            params['f_I'] = filters
            debug(tag, 'Applied industry filters', query['industry'])
        
        
        params['start'] = str(self.start)

        self.start += 25

        parsed = parsed._replace(query=urlencode(params))
        return parsed.geturl()

    
    def start_requests(self):
        config = self.load_config('config.json')  # Load configuration
        queries = self.load_query()
        for query in queries:
            self.start = 0
            for i in range(config['num_pages']):
                url = self.build_search_url(query)
                yield scrapy.Request(url, callback=self.parse, headers=config['headers'], meta={'config': config, 'query': query})
    
    def parse(self, response):
        config = response.meta['config']
        query = response.meta['query']
        joblist = []
        # Extracting job cards
        cards = response.css('div.base-search-card__info')
        print(len(cards))
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

            # Get the job description asynchronously
            yield response.follow(jobLink, callback=self.parse_description,  headers=config['headers'], meta={'job_item': job_item, 'config': config})

    def parse_description(self, response):
        config = response.meta['config']
        job_item = response.meta['job_item']
        description_div = response.css('div.description__text.description__text--rich')
        job_insight = response.css('span.job-details-jobs-unified-top-card__job-insight-view-model-secondary::text').get(default='not-found').strip()   
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
        job_item['job_insight'] = job_insight
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
