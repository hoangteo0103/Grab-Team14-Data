import scrapy
from urllib.parse import quote
from datetime import datetime
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from ..items import JobItem
import json
from urllib.parse import urlparse, urlencode
from ..utils.constants import *
from ..utils.logger import debug
from ..settings import *
from dotenv import load_dotenv
from ..filters.filters import *
load_dotenv()


class VietnamworksSpyder(scrapy.Spider):
    name = 'vietnamworks-scraper'

    def __init__(self, *args, **kwargs):
     self.queries = kwargs.get('queries')
     self.config = kwargs.get('config')
     self.page = 0 # Start page
     self.stop = False 
     
        
    def build_search_body(self, query):
        if query is None:
            return {}

        body = {}

        body["userId"] = 0

        if query.get('keywords') is not None and len(query['keywords']) > 0:
            body['query'] = query['keywords']
        filter = [] 
        if query.get('location') is not None and len(query['location']) > 0:
            location = query['location'].upper().replace(" ", "_")
            filter.append( {"field": "workingLocations.cityId", "value": CityFilter[location].value })
          
        if query.get('type') is not None and len(query['type']) > 0:
            filter.append( {"field": "typeWorkingId", "value": TypeFilters[query['type'].value ]})
        
        if query.get('experience') is not None and len(query['experience']) > 0:
            filter.append( {"field": "jobLevelId", "value": ExperienceLevelFilters[query['experience'].value]})

        if query.get('industry') is not None and len(query['industry']) > 0:
            for industryQ in query['industry']:
                industries = IndustryFilter[industryQ].value.split(".")
                values = []
                for industry in industries:
                    values.append({
                        "parentId": int(industry),
                        "childrenIds" : [-1]
                    })
            
            json_str = json.dumps(values)

            # Escape the double quotes
            escaped_json_str = json_str.replace('"', '\\"')

            # Wrap it in double quotes
            final_str = f'"{escaped_json_str}"'
            filter.append( {"field": "jobFunction", "value": final_str})
        

        body["page"] = self.page
        body["order"] = []
        body["hitsPerPage"] = 10000
        body["ranges"] = []
        body["retrieveFields"] = [
              "address",
    "benefits",
    "jobTitle",
    "salaryMax",
    "isSalaryVisible",
    "jobLevelVI",
    "isShowLogo",
    "salaryMin",
    "companyLogo",
    "userId",
    "jobLevel",
    "jobLevelId",
    "jobId",
    "jobUrl",
    "companyId",
    "approvedOn",
    "isAnonymous",
    "alias",
    "expiredOn",
    "industries",
    "workingLocations",
    "services",
    "companyName",
    "salary",
    "onlineOn",
    "simpleServices",
    "visibilityDisplay",
    "isShowLogoInSearch",
    "priorityOrder",
    "skills",
    "profilePublishedSiteMask",
    "jobDescription",
    "jobRequirement",
    "prettySalary",
    "requiredCoverLetter",
    "languageSelectedVI",
    "languageSelected",
    "languageSelectedId"
            ]
        body["filter"] = filter
        self.page += 1
        print(body)
        return body

    def load_config(self, path):
        with open(path) as f:
            return json.load(f)
        
    def start_requests(self):
        for query in self.queries:
            print(query)
            self.page = 0
            for i in range(self.config['num_pages']):
                if self.stop:
                    break
                body = self.build_search_body(query)
                yield scrapy.Request(JOBS_SEARCH_URL,callback=self.parse, method="POST" ,  body= json.dumps(body) ,meta={'config': self.config, 'query': query}, headers=self.config["headers"], dont_filter=True)
    
    def parse(self, response):
        config = response.meta['config']
        query = response.meta['query']

        data_string = response.body.decode('utf-8')

        # Convert the JSON string to a dictionary
        data_dict = json.loads(data_string)

        # Get the jobs from the dictionary
        if len(data_dict['data']) == 0:
            self.stop = True
        print(len(data_dict['data']))
        for job_dict in data_dict['data']:
            industry = None
            try:
                industry = IndustryFilter(str(job_dict['jobFunction']['parentId'])).name
            except:
                pass 
            if industry is None:
                try:
                    industry = job_dict['jobFunction']['parentName']
                except:
                    industry = job_dict['groupJobFunctionsV3']['groupJobFunctionV3Name']
            job_item = {
                'title': job_dict['jobTitle'],
                'company': job_dict['companyName'],
                'date': job_dict['approvedOn'],
                'jobLink': job_dict['jobUrl'],
                'description': job_dict['jobDescription'],
                'companyLink': job_dict['companyLogo'],
                'companyLocation': job_dict['address'],
                'companyImageUrl': job_dict['companyLogo'],
                'experience': ExperienceLevelFilters(str(job_dict['jobLevelId'])).name,
                'type': TypeFilters(str(job_dict['typeWorkingId'])).name ,
                'requirements': job_dict['jobRequirement'],
                'industry': industry,
                'query': query,
            }
            yield job_item
