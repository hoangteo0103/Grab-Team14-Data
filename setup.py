from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.twisted import TwistedScheduler

from linkedin_scraper.linkedin_scraper.spiders.linkedin_spyder import LinkedInScraperSpider 
from topcv_scraper.topcv_scraper.spiders.topcv_spyder import TopcvScraperSpider
import json, os
from dotenv import load_dotenv
from pymongo import MongoClient

global db, queries, config 
load_dotenv()

def load_config(file_name):
    # Load the config file
    with open(file_name) as f:
        return json.load(f)


def setup_db():
    # Setup the database
    client = MongoClient(os.getenv('MONGODB_URI'))
    global db
    db = client["Grab-Data"]

def load_query():
    query_collection = db["search_queries"]
    queries = query_collection.find()
    return queries

def setup():
    setup_db()
    global queries, config
    config = load_config('config.json')
    queries = load_query()

    return db, queries, config
