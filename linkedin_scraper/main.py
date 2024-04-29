from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.twisted import TwistedScheduler

from linkedin_scraper.spiders.linkedin_spyder import LinkedInScraperSpider # your spider

process = CrawlerProcess(get_project_settings())
scheduler = TwistedScheduler()
scheduler.add_job(process.crawl, 'interval', args=[LinkedInScraperSpider], seconds=60*60*24)
scheduler.start()
process.start(False)