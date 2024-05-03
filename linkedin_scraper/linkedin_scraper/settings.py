# settings.py
import os
BOT_NAME = 'linkedin_scraper'

SPIDER_MODULES = ['linkedin_scraper.spiders']
NEWSPIDER_MODULE = 'linkedin_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1

AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

RETRY_HTTP_CODES = [429]

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'linkedin_scraper.pipelines.LinkedinScraperPipeline': 150,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'linkedin_scraper.middlewares.TooManyRequestsRetryMiddleware': 543,
}