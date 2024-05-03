import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from apscheduler.schedulers.twisted import TwistedScheduler
import indeed_scraper
from setup import setup
from dotenv import load_dotenv

load_dotenv()

db, queries, config = setup()

def transform_query(query):

    query_indeed = {
        'keywords': query.get('keywords', ''),
        'location': query.get('location', ''),
        'time': query.get('time', ''),
        'relevance': query.get('relevance', ''),
        'type': query.get('type', '').lower().replace('_', ' '),
        '_id':  query.get('_id', '')

    }

    return query_indeed


def crawler_indeed():
    queries_indeed = [transform_query(q) for q in queries]
    scheduler = TwistedScheduler()
    indeed_scraper.start_scaper(config=config, queries=queries_indeed)
    scheduler.add_job(indeed_scraper.start_scaper, 'interval', kwargs={'config': config, 'queries': queries_indeed}, seconds=60*60*24)
    scheduler.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run web crawlers.")

    args = parser.parse_args()
    crawler_indeed()
