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

load_dotenv()

db, queries, config = setup()

def transform_query(query):
    industries = query.get('industry', [])

    for industry in industries:
        if industry not in IndustryFilters.__members__:
            raise ValueError(f'Invalid industry: {industry}')
    query_linkedin = {
        'keywords': query.get('keywords', ''),
        'location': query.get('location', ''),
        'time': 'r' + str(int(query.get('time', '0')) / 86400),
        'relevance': query.get('relevance', [''])[0],
        'type': query.get('type', [''])[0],
        'experience': next((key for key in ExperienceLevelFilters.__members__.keys() if key[0] == query.get('experience', [''])[0]), ''),
        'industry': industries
    }

    return query_linkedin

def crawler_linkedin():
    queries_linkedin= zip(*(transform_query(q) for q in queries))
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