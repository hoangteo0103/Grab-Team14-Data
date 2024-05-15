import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()
    job_url = scrapy.Field()
    job_description = scrapy.Field()
    company_link = scrapy.Field()
    company_location = scrapy.Field()
    company_image_url = scrapy.Field()
    working_type = scrapy.Field()
    query = scrapy.Field()