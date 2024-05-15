import argparse
from scrapy.crawler import CrawlerProcess
from apscheduler.schedulers.twisted import TwistedScheduler
from topcv_scraper.spiders.topcv_spyder import TopcvScraperSpider
from scrapy.utils.project import get_project_settings
from setup import setup
from dotenv import load_dotenv
import datetime

load_dotenv()

db, queries, config = setup()

def transform_query(queries):
    
    queries_topcv = []
    for query in queries:
        print(query)
        if query.get('last_crawled_topcv', None) is not None and (datetime.datetime.now() - query.get('last_crawled_topcv')).days < 1:
            print('Skip crawling topcv for query:', query.get('_id', ''), 'because it was crawled today')
            continue


        query_topcv = {}

        if 'keywords' in query:
            query_topcv['keywords'] = query['keywords']

        if 'location' in query:
            query_topcv['location'] = query['location']

        if 'relevance' in query:
            query_topcv['relevance'] = query['relevance']

        if 'type' in query:
            query_topcv['type'] = query['type']

        if 'experience' in query:
            query_topcv['experience'] = query['experience']

        if 'industry' in query:
            query_topcv['industry'] = query['industry']

        query_topcv['_id'] = query.get('_id', '')
        queries_topcv.append(query_topcv)
    return queries_topcv



def crawler_topcv():
    queries_topcv = transform_query(queries)
    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    process.crawl(TopcvScraperSpider, config=config, queries=queries_topcv)
    scheduler.add_job(process.crawl, 'interval', args=[TopcvScraperSpider], kwargs={'config': config, 'queries': queries_topcv}, seconds=60*60*24)
    scheduler.start()
    process.start(False)

if __name__ == '__main__':

    crawler_topcv()