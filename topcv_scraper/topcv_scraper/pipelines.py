# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from pymongo import MongoClient
from .filters.filters import *
import datetime

class TopcvScraperPipeline:
    def __init__(self):
        client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = client["Grab-Data"]
        self.job_collection = self.db["jobs_topcv_1"]
    def process_item(self, item, spider):
        self.query_collection = self.db["search_queries"]


        query = self.query_collection.find_one({'_id': item['query']['_id']})

        query['last_crawl_topcv'] = datetime.datetime.now()

        self.query_collection.update_one({'_id': item['query']['_id']}, {'$set': query})
        if self.job_collection.find_one({'job_url': item['job_url'], 'company': item['company'], 'title': item['title'], 'date': item['date']}) is not None:
            job = self.job_collection.find_one({'job_url': item['job_url'], 'company': item['company'], 'title': item['title'], 'date': item['date']})
            if 'industry' in item['query']:
                for code in item['query']['industry']:
                    if code not in job['industry']:
                        job['industry'].append(code)
            
            if 'type' not in job and 'type' in item['query']:
                job['type'] = item['query']['type']

            if 'experience' not in job and 'experience' in item['query']:
                job['experience'] = item['query']['experience']

            if 'working_type' not in job and 'working_type' in item:
                job['working_type'] = item['working_type']

            self.job_collection.update_one({'job_url': item['job_url'], 'company': item['company'], 'title': item['title'], 'date': item['date']}, {'$set': job})
            return item
        industries = []
        if 'industry' in item['original_query']:
            for code in item['original_query']['industry']:
                industries.append(code)
        
        self.job_collection.insert_one(
            {
                'title': item['title'],
                'company': item['company'],
                'location': item['location'],
                'date': item['date'] if 'date' in item else None,
                'job_url': item['job_url'],
                'job_description': item['job_description'],
                'company_link': item['company_link'],
                'company_location': item['company_location'],
                'industry': industries,
                'type': item['query']['type'] if 'type' in item['query'] else None,
                'experience': item['query']['experience'] if 'experience' in item['query'] else None,
                'keywords': item['query']['keywords'] if 'keywords' in item['query'] else None,
                'time': item['query']['time'] if 'time' in item['query'] else None,
            }
        )
        return item
