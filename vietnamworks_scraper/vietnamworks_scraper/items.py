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
    jobLink = scrapy.Field()
    description = scrapy.Field()
    companyLink = scrapy.Field()
    companyLocation = scrapy.Field()
    companyImageUrl = scrapy.Field()
    type = scrapy.Field()
    experience = scrapy.Field()
    requirements = scrapy.Field()
