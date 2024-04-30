# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()
    job_url = scrapy.Field()
    job_description = scrapy.Field()
    company_link = scrapy.Field()
    company_location = scrapy.Field()
    query = scrapy.Field()
