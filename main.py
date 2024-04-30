from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.twisted import TwistedScheduler


from linkedin_scraper.linkedin_scraper.spiders.linkedin_spyder import LinkedInScraperSpider

from topcv_scraper.topcv_scraper.spiders.topcv_spyder import TopcvScraperSpider
from indeed_scraper import indeed_scraper
import json, os
from dotenv import load_dotenv
from pymongo import MongoClient
from setup import setup
from linkedin_scraper.linkedin_scraper.filters import *

global db, queries, config

load_dotenv()


db, queries, config = setup()

def query_transform_pipeline_linkedin(queries):
    queries_linkedin = []
    for query in queries:
        query_linkedin = {}
        query_linkedin['keywords'] = query['keywords'] 
        query_linkedin['location'] = query['location']
        query_linkedin['time'] = 'r' + query['time']
        query_linkedin['relevance'] = query['relevance'][0]           
        query_linkedin['type'] = query['type'][0]

        for key in ExperienceLevelFilters.keys():
            if key[0] == query['experience'][0]:
                query_linkedin['experience'] = key
                break
        queries_linkedin.append(query_linkedin)
    return queries_linkedin

def query_transform_pipeline_topcv(queries):
    queries_topcv = []
    for query in queries:
        query_topcv = {}
        query_topcv['keywords'] = query['keywords']
        query_topcv['location'] = query['location']
        queries_topcv['industry'] = query['industry']
        query_topcv['relevance'] = query['relevance']
        query_topcv['type'] = query['type']
        query_topcv['experience'] = query['experience']
        queries_topcv.append(query_topcv)
    return queries_topcv

def query_transform_pipeline_indeed(queries):
    queries_indeed = []
    for query in queries:
        query_indeed = {}
        query_indeed['keywords'] = query['keywords']
        query_indeed['location'] = query['location']
        query_indeed['time'] = query['time']
        query_indeed['relevance'] = query['relevance']
        query_indeed['type'] = query['type'].lower().replace('_', ' ')
        queries_indeed.append(query_indeed)
    return queries_indeed



def query_transform_pipeline(queries):
    for query in queries:
        query['keywords'] = query.get('keywords','')
        query['location'] = query.get('location','')
        query['time'] = query.get('time','')
        query['relevance'] = query.get('relevance','')
        query['type'] = query.get('type','')
        query['experience'] = query.get('experience','')

    queries_linkedin = query_transform_pipeline_linkedin(queries)
    queries_topcv = query_transform_pipeline_topcv(queries)
    queries_indeed = query_transform_pipeline_indeed(queries)

    return queries_linkedin, queries_topcv, queries_indeed


def crawler():
    queries_l, queries_t, queries_i  = query_transform_pipeline(queries)

    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    scheduler.add_job(process.crawl, 'interval', args=[LinkedInScraperSpider], kwargs= {'config': config, 'queries': queries_l}, seconds=60)
    scheduler.add_job(process.crawl, 'interval', args=[TopcvScraperSpider], kwargs= {'config': config, 'queries': queries_t}, seconds=60)
    scheduler.add_job(indeed_scraper.start_scaper, 'interval', kwargs={'config':config, 'queries':queries_i}, seconds=60)
    scheduler.start()
    process.start(False)

if __name__ == '__main__':
    crawler()