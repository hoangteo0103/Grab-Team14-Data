import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.utils.project import get_project_settings
from linkedin_scraper.spiders.linkedin_spyder import LinkedInScraperSpider
from linkedin_scraper.filters.filters import ExperienceLevelFilters
from linkedin_scraper.filters.filters import IndustryFilters
from setup import setup
from dotenv import load_dotenv
import datetime

load_dotenv()

db, queries, config = setup()

def transform_query(queries):
    queries_linkedin = []
    for query in queries:
        if query.get('last_crawled_linkedin', None) is not None and (datetime.datetime.now() - query.get('last_crawled_linkedin')).days < 1:
            print('Skip crawling linkedin for query:', query.get('_id', ''), 'because it was crawled today')
            continue
        industries = query.get('industry', [])

        for industry in industries:
            if industry not in IndustryFilters.__members__:
                raise ValueError(f'Invalid industry: {industry}')
            
        query_linkedin = {}


        if 'keywords' in query:
            query_linkedin['keywords'] = query['keywords']
        if 'location' in query:
            query_linkedin['location'] = query['location']
        
        if 'time' in query:
            query_linkedin['time'] = 'r' + str(int(query['time']) / 86400)
        
        if 'relevance' in query:
            query_linkedin['relevance'] = query['relevance']

        if 'type' in query:
            query_linkedin['type'] = query['type']

        if 'experience' in query:
            query_linkedin['experience'] = next((key for key in ExperienceLevelFilters.__members__.keys() if key[0] == query['experience']), '')

        if 'industry' in query:
            query_linkedin['industry'] = []
            for industry in query['industry']:
                query_linkedin['industry'].append(IndustryFilters.getValueFromKey(industry))

        query_linkedin['_id'] = query.get('_id', '')
        queries_linkedin.append(query_linkedin)

    return queries_linkedin

def crawler_linkedin():
    queries_linkedin= transform_query(queries)
    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    process.crawl(LinkedInScraperSpider, config=config, queries=queries_linkedin)
    scheduler.add_job(process.crawl, 'interval', args=[LinkedInScraperSpider], kwargs={'config': config, 'queries': queries_linkedin}, seconds=60 * 60)
    scheduler.start()
    process.start(False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run web crawlers.")

    args = parser.parse_args()
    crawler_linkedin()