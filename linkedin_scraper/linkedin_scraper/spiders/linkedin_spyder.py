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
from dotenv import load_dotenv

load_dotenv()


class LinkedInScraperSpider(scrapy.Spider):
    name = 'linkedin-scraper'

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
        self.config = self.load_config('config.json')
        self.queries= self.config['search_queries']
        for query in self.queries:
            self.start = 0
            for i in range(self.config['num_pages']):
                if self.stop:
                    break
                url = self.build_search_url(query)
                yield scrapy.Request(url, callback=self.parse, headers=self.config['headers'], meta={'config': self.config, 'query': query})
    
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
            company_link = card.css('h4 a::attr(href)').get(default='not-found')
            company_location = card.css('.job-search-card__location::text').get(default='not-found').strip()
            location = card.css('span.job-search-card__location::text').get(default='not-found').strip()
            entity_urn = card.xpath('../@data-entity-urn').get(default='not-found')
            job_posting_id = entity_urn.split(':')[-1]
            job_url = f'https://www.linkedin.com/jobs/view/{job_posting_id}/'
            date_tag = card.css('time.job-search-card__listdate').attrib.get('datetime', '')
            date_tag_new = card.css('time.job-search-card__listdate--new').attrib.get('datetime', '')
            date = date_tag if date_tag else date_tag_new

            # Create a job item without description
            job_item = {
                'title': title,
                'company': company,
                'company_link': company_link,
                'company_location': company_location,
                'location': location,
                'date': date,
                'job_url': job_url,
                'query': query,
            }

            # Get the job description asynchronously
            yield response.follow(job_url, callback=self.parse_job_description,  headers=config['headers'], meta={'job_item': job_item, 'config': config})

    def parse_job_description(self, response):
        config = response.meta['config']
        job_item = response.meta['job_item']
        description_div = response.css('div.description__text.description__text--rich')
        job_insight = response.css('span.job-details-jobs-unified-top-card__job-insight-view-model-secondary::text').get(default='not-found').strip()   
        if description_div:
            # Remove unwanted elements
            for element in description_div.css('span, a'):
                element.extract()

            # Get the cleaned text
            job_description = '\n'.join(description_div.xpath('.//text()').extract()).strip()
            job_description = job_description.replace('\n\n', '')
            job_description = job_description.replace('::marker', '-')
            job_description = job_description.replace('-\n', '- ')
            job_description = job_description.replace('Show less', '').replace('Show more', '')
        else:
            job_description = "Could not find Job Description"
        job_item['job_insight'] = job_insight
        job_item['job_description'] = job_description
        yield job_item

    def remove_irrelevant_jobs(self, joblist, config):
        new_joblist = [job for job in joblist if not any(word.lower() in job['job_description'].lower() for word in config['desc_words'])]   
        new_joblist = [job for job in new_joblist if not any(word.lower() in job['title'].lower() for word in config['title_exclude'])] if len(config['title_exclude']) > 0 else new_joblist
        new_joblist = [job for job in new_joblist if any(word.lower() in job['title'].lower() for word in config['title_include'])] if len(config['title_include']) > 0 else new_joblist
        new_joblist = [job for job in new_joblist if self.safe_detect(job['job_description']) in config['languages']] if len(config['languages']) > 0 else new_joblist
        new_joblist = [job for job in new_joblist if not any(word.lower() in job['company'].lower() for word in config['company_exclude'])] if len(config['company_exclude']) > 0 else new_joblist
        return new_joblist

    def safe_detect(self, text):
        try:
            return detect(text)
        except LangDetectException:
            return 'en'
