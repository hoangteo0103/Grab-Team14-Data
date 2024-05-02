import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from linkedin_scraper.linkedin_scraper import settings as linkedin_settings

from apscheduler.schedulers.twisted import TwistedScheduler
from linkedin_scraper import crawl
from topcv_scraper.topcv_scraper.spiders.topcv_spyder import TopcvScraperSpider
from indeed_scraper import indeed_scraper
from linkedin_scraper.linkedin_scraper.filters.filters import ExperienceLevelFilters
from setup import setup
from dotenv import load_dotenv

load_dotenv()

db, queries, config = setup()

def transform_query(query):
    query_linkedin = {
        'keywords': query.get('keywords', ''),
        'location': query.get('location', ''),
        'time': 'r' + str(int(query.get('time', '0')) / 86400),
        'relevance': query.get('relevance', [''])[0],
        'type': query.get('type', [''])[0],
        'experience': next((key for key in ExperienceLevelFilters.__members__.keys() if key[0] == query.get('experience', [''])[0]), '')
    }
    
    query_topcv = {
        'keywords': query.get('keywords', ''),
        'location': query.get('location', ''),
        'industry': query.get('industry', ''),
        'relevance': query.get('relevance', ''),
        'type': query.get('type', ''),
        'experience': query.get('experience', '')
    }

    query_indeed = {
        'keywords': query.get('keywords', ''),
        'location': query.get('location', ''),
        'time': query.get('time', ''),
        'relevance': query.get('relevance', ''),
        'type': query.get('type', '').lower().replace('_', ' ')
    }

    return query_linkedin, query_topcv, query_indeed


def crawler_topcv():
    _, queries_topcv, _ = zip(*(transform_query(q) for q in queries))
    process = CrawlerProcess(get_project_settings())
    scheduler = TwistedScheduler()
    process.crawl(TopcvScraperSpider, kwargs={'config': config, 'queries': queries_topcv})
    scheduler.add_job(process.crawl, 'interval', args=[TopcvScraperSpider], kwargs={'config': config, 'queries': queries_topcv}, seconds=60*60*24)
    scheduler.start()
    process.start(False)

def crawler_indeed():
    _, _, queries_indeed = zip(*(transform_query(q) for q in queries))
    scheduler = TwistedScheduler()
    scheduler.add_job(indeed_scraper.start_scaper, 'interval', kwargs={'config': config, 'queries': queries_indeed}, seconds=60*60*24)
    scheduler.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run web crawlers.")
    parser.add_argument("crawler", choices=["linkedin", "topcv", "indeed", "all"], help="Specify which crawler to run.")

    args = parser.parse_args()

    if args.crawler == "linkedin":
        crawl.crawler_linkedin()
    elif args.crawler == "topcv":
        crawler_topcv()
    elif args.crawler == "indeed":
        crawler_indeed()
    elif args.crawler == "all":
        crawler_linkedin()
        crawler_topcv()
        crawler_indeed()
