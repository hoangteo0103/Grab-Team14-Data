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
class LinkedinScraperPipeline:
    def __init__(self):
        client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = client["Grab-Data"]
        self.job_collection = self.db["jobs_linkedin"]
    def process_item(self, item, spider):
        self.query_collection = self.db["search_queries"]


        query = self.query_collection.find_one({'_id': item['query']['_id']})

        query['last_crawled_linkedin'] = datetime.datetime.now()

        # self.query_collection.update_one({'_id': item['query']['_id']}, {'$set': query})
        if self.job_collection.find_one({'jobLink': item['jobLink']}) is not None:
            job = self.job_collection.find_one({'jobLink': item['jobLink']})
            if 'date' not in job:
                job['date'] = item['date']
            if 'industry' in item['query']:
                for code in item['query']['industry']:
                    if code not in job['industry']:
                        job['industry'].append(code)
            
            if 'type' not in job and 'type' in item['query']:
                job['type'] = item['query']['type']

            if 'experience' not in job and 'experience' in item['query']:
                job['experience'] = item['query']['experience']

            if 'workingMode' not in job and 'workingMode' in item:
                job['workingMode'] = item['workingMode']
            job['description'] = item['description']
            job['companyLink'] = item['companyLink']

            self.job_collection.update_one({'jobLink': item['jobLink']}, {'$set': job})
            return item
        industries = []
        if 'industry' in item['query']:
            for code in item['query']['industry']:
                industries.append(code)

        
        self.job_collection.insert_one(
            {
                'title': item['title'],
                'company': item['company'],
                'location': query['location'],
                'date': item['date'],
                'jobLink': item['jobLink'],
                'description': item['description'],
                'companyLink': item['companyLink'],
                'companyLocation': item['companyLocation'],
                'industry': industries,
                'type': item['query']['type'] if 'type' in item['query'] else None,
                'experience': item['query']['experience'] if 'experience' in item['query'] else None,
                'keywords': item['query']['keywords'] if 'keywords' in item['query'] else None,
                'time': item['query']['time'] if 'time' in item['query'] else None,
                'companyImageUrl': item['companyImageUrl'],
                'workingMode': item['workingMode'],
                'platform': 'Linkedin'
            }
        )
        return item
