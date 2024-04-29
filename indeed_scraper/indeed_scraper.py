from requests_html import HTMLSession
import csv
from bs4 import BeautifulSoup
from constants import *

from pymongo import MongoClient
import os
import json
from urllib.parse import urlparse, urlencode
from dotenv import load_dotenv
from logger import debug


def job_data_get(s, url: str) -> tuple:
    # return the elements for each job card
    r = s.get(url)
    return r.html.find('ul.pagination-list a[aria-label=Next]'), r.html.find('div.job_seen_beacon')

def parse_html_job_desc(s, job_dict) -> dict:
    job_desc_req = s.get(job_dict['link'])
    job_desc_soup = BeautifulSoup(job_desc_req.text, 'html.parser')
    with open('job_desc.html', 'w', encoding='utf-8') as f:
        f.write(job_desc_soup.prettify())
    job_type = []

    for key in map_english:
        if job_desc_soup.find('div', attrs={'data-testid': map_english[key]+'-title'}):
            job_type.append(key)

    job_dict['type'] = job_type

    div = job_desc_soup.find('div', class_='jobsearch-jobDescriptionText')
    if div:
        # Remove unwanted elements
        for element in div.find_all(['span', 'a']):
            element.decompose() 

        # Replace bullet points
        for ul in div.find_all('ul'):
            for li in ul.find_all('li'):
                li.insert(0, '-')

        text = div.get_text(separator='\n').strip()
        text = text.replace('\n\n', '')
        text = text.replace('::marker', '-')
        text = text.replace('-\n', '- ')
        job_dict['description'] = text

    return job_dict

def parse_html(s, job) -> dict:
    soup = BeautifulSoup(job.html, 'html.parser')

    companyname = soup.find('span', attrs={'data-testid': 'company-name'})
    companylocation = soup.find('div', attrs={'data-testid': 'text-location'})
    job_dict = {'title': job.find('h2 > a')[0].text,
                'link': 'https://vn.indeed.com/viewjob?jk=' + job.find('h2 > a')[0].attrs['data-jk'] if job.find('h2 > a') else 'no link',
                'company': companyname.text if companyname else 'no company name',
                'location': companylocation.text if companylocation else 'no location',
                }
    
    return parse_html_job_desc(s, job_dict)

def load_config(file_name):
    # Load the config file
    with open(file_name) as f:
        return json.load(f)

def load_query():
    query_collection = db["search_queries"]
    queries = query_collection.find()
    return queries
    
def build_search_url(query):
    if query is None:
        return JOB_BASE_URL
    tag = f'[{query.get('keywords')}][{query.get('location')}]'
    parsed = urlparse(JOB_BASE_URL)
    params = {}

    if query.get('keywords') is not None:
        params['q'] = query['keywords']

    if query.get('location') is not None:
        params['l'] = query['location']


    if query.get('time') is not None:
        params['fromage'] = query['time']
        debug(tag, 'Applied time filter', query['time'])
    
    if query.get('relevance') is not None:
        params['sort'] = query['relevance']
        debug(tag, 'Applied relevance filter', query['relevance'])
        
    if query.get('type') is not None:
        filters = ','.join(e for e in query['type'])
        params['jt'] = filters
        debug(tag, 'Applied type filters', query['type'])
    
    global start
    params['start'] = str(start)

    start += 25

    parsed = parsed._replace(query=urlencode(params))
    return parsed.geturl()    

def add_job_to_db(job_dict):
    print(job_dict)
    job_collection = db["job_indeed"]
    if job_collection.find_one({'title': job_dict['title'], 'company': job_dict['company'], 'location': job_dict['location']}):
        print('Job already exists')
    else:
        job_collection.insert_one(job_dict)


def start_requests():
    s = HTMLSession()
    queries = load_query()
    for query in queries:
        start = 0
        for i in range(config['num_pages']):
            url = build_search_url(query)
            print(url)
            while True:
                jobs = job_data_get(s, url)
                for job in jobs[1]:
                    add_job_to_db(parse_html(s, job))
                try:
                    url = baseurl + jobs[0][0].attrs['href']
                    print(url)
                except IndexError as err:
                    print(err)
                    break

load_dotenv()
start = 0 
client = MongoClient(os.getenv('MONGODB_URI'))
db = client["Grab-Data"]
start = 0 # Start page
job_search = 'python'
baseurl = JOB_BASE_URL
config = load_config('config.json')

if __name__ == '__main__':
    
    start_requests()
        