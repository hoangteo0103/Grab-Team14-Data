# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os 
from pymongo import MongoClient
from .filters import *

class LinkedinScraperPipeline:
    def __init__(self):
        client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = client["Grab-Data"]
        self.job_collection = self.db["jobs"]
    def process_item(self, item, spider):
        if self.job_collection.find_one({'jobLink': item['jobLink'], 'company': item['company'], 'title': item['title'], 'date': item['date']}) is not None:
            return item
        
        industries = []
        if 'industry' in item['query']:
            for code in item['query']['industry']:
                industry_name = IndustryFilters(code).name
                if industry_name:
                    industries.append(industry_name)

        
        self.job_collection.insert_one(
            {
                'title': item['title'],
                'company': item['company'],
                'location': item['location'],
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
            }
        )
        return item
