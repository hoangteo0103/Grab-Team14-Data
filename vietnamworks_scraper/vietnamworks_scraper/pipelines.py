# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import datetime 
import os
from pymongo import MongoClient
from datetime import datetime
class VietnamworksScraperPipeline:
    
    def __init__(self):
        client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = client["Grab-Data"]
        self.job_collection = self.db["jobs"]
    def process_item(self, item, spider):
        self.query_collection = self.db["search_queries"]

        query = self.query_collection.find_one({'_id': item['query']['_id']})

        # query['last_crawled_vietnamworks'] = datetime.datetime.now()

        # self.query_collection.update_one({'_id': item['query']['_id']}, {'$set': query})
        if self.job_collection.find_one({'jobLink': item['jobLink']}) is not None:
            job = self.job_collection.find_one({'jobLink': item['jobLink']})
            if 'industry' in item['industry']:
                for code in item['query']['industry']:
                    if code not in job['industry']:
                        job['industry'].append(code)
            
            if 'type' not in job and 'type' in item['query']:
                job['type'] = item['query']['type']

            if 'experience' not in job and 'experience' in item['query']:
                job['experience'] = item['query']['experience']
            if 'requirements' not in job and 'requirements' in item:
                job['requirements'] = item['requirements']
            if 'date' not in job:
                date_obj = datetime.fromisoformat(item['date'])
                job['date'] = date_obj
            
            print("Update job")
            self.job_collection.update_one({'jobLink': item['jobLink'], 'company': item['company'], 'title': item['title'], 'date': item['date']}, {'$set': job})
            return item
        
        print("Insert job")
        date_obj = datetime.fromisoformat(item['date'])
        self.job_collection.insert_one(
            {
                'title': item['title'],
                'company': item['company'],
                'location': query['location'],
                'date': date_obj,
                'jobLink': item['jobLink'],
                'applyLink': '',
                'description': item['description'],
                'companyLink': item['companyLink'],
                'companyLocation': item['companyLocation'],
                'companyImageUrl': item['companyImageUrl'],
                'industry': [item['industry']],
                'type': item['type'],
                'requirements': item['requirements'],
                'experience': item['experience'],
                'platform': 'Vietnamworks'
            })
        return item