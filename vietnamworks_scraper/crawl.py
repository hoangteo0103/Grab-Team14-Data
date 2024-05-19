import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.utils.project import get_project_settings
from vietnamworks_scraper.spiders.vietnamworks_spyder import VietnamworksSpyder
from setup import setup
from dotenv import load_dotenv
import datetime


load_dotenv()

db, queries, config = setup()

def transform_query(queries):
    queries_vietnamworks = []
    for query in queries:
        if query.get('last_crawled_vietnamworks', None) is not None and (datetime.datetime.now() - query.get('last_crawled_vietnamworks')).days < 1:
            print('Skip crawling Vietnamworks for query:', query.get('_id', ''), 'because it was crawled today')
            continue
        industries = query.get('industry', [])
            
        query_vietnamworks = {}


        if 'keywords' in query:
            query_vietnamworks['keywords'] = query['keywords']
        if 'location' in query:
            query_vietnamworks['location'] = query['location']
        
        if 'type' in query:
            query_vietnamworks['type'] = query['type']

        if 'experience' in query:
            query_vietnamworks['experience'] = query['experience']

        if 'industry' in query:
            query_vietnamworks['industry'] = query['industry']

        query_vietnamworks['_id'] = query.get('_id', '')
        queries_vietnamworks.append(query_vietnamworks)

    return queries_vietnamworks

def crawler_linkedin():
    queries_vietnamworks= transform_query(queries)
    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    process.crawl(VietnamworksSpyder, config=config, queries=queries_vietnamworks)
    scheduler.add_job(process.crawl, 'interval', args=[VietnamworksSpyder], kwargs={'config': config, 'queries': queries_vietnamworks}, seconds=60 * 60)
    scheduler.start()
    process.start(False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run web crawlers.")

    args = parser.parse_args()
    crawler_linkedin()