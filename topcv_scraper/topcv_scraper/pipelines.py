# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from pymongo import MongoClient


class TopcvScraperPipeline:
    def __init__(self):
        client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = client["Grab-Data"]
        self.job_collection = self.db["jobs_topcv"]
    def process_item(self, item, spider):
        if self.job_collection.find_one({'job_url': item['job_url'], 'company': item['company'], 'title': item['title']}) is not None:
            return item
        
        
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
                'industry': [],
                'type': item['query']['type'] if 'type' in item['query'] else None,
                'experience': item['query']['experience'] if 'experience' in item['query'] else None,
                'keywords': item['query']['keywords'] if 'keywords' in item['query'] else None,
                'time': item['query']['time'] if 'time' in item['query'] else None,
            }
        )
        return item
