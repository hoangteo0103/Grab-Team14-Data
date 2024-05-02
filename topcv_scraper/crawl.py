import argparse
from scrapy.crawler import CrawlerProcess
from apscheduler.schedulers.twisted import TwistedScheduler
from topcv_scraper.spiders.topcv_spyder import TopcvScraperSpider
from scrapy.utils.project import get_project_settings
from setup import setup
from dotenv import load_dotenv

load_dotenv()

db, queries, config = setup()

def transform_query(query):
    
    query_topcv = {
        'keywords': query.get('keywords', ''),
        'location': query.get('location', ''),
        'industry': query.get('industry', ''),
        'relevance': query.get('relevance', ''),
        'type': query.get('type', ''),
        'experience': query.get('experience', '')
    }

    return query_topcv


def crawler_topcv():
    queries_topcv = zip(*(transform_query(q) for q in queries))
    process = CrawlerProcess(settings=get_project_settings())
    scheduler = TwistedScheduler()
    process.crawl(TopcvScraperSpider, kwargs={'config': config, 'queries': queries_topcv})
    scheduler.add_job(process.crawl, 'interval', args=[TopcvScraperSpider], kwargs={'config': config, 'queries': queries_topcv}, seconds=60*60*24)
    scheduler.start()
    process.start(False)

if __name__ == '__main__':

    crawler_topcv()