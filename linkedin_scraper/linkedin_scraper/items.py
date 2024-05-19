import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()
    jobLink = scrapy.Field()
    description = scrapy.Field()
    companyLink = scrapy.Field()
    companyLocation = scrapy.Field()
    companyImageUrl = scrapy.Field()
    workingMode = scrapy.Field()
    query = scrapy.Field()