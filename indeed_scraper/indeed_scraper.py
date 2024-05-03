from requests_html import HTMLSession
import concurrent.futures
from bs4 import BeautifulSoup
from constants import *

from pymongo import MongoClient
import os
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
        job_dict['job_description'] = text

    return job_dict

def parse_html(s, job, query) -> dict:
    soup = BeautifulSoup(job.html, 'html.parser')

    companyname = soup.find('span', attrs={'data-testid': 'company-name'})
    companylocation = soup.find('div', attrs={'data-testid': 'text-location'})
    job_dict = {'title': job.find('h2 > a')[0].text,
                'link': 'https://vn.indeed.com/viewjob?jk=' + job.find('h2 > a')[0].attrs['data-jk'] if job.find('h2 > a') else 'no link',
                'company': companyname.text if companyname else 'no company name',
                'location': companylocation.text if companylocation else 'no location',
                'query': query,
                }
    
    return parse_html_job_desc(s, job_dict)
    
def build_search_url(query):
    if query is None:
        return JOB_BASE_URL
    parsed = urlparse(JOB_BASE_URL)
    params = {}

    params['l'] = "Việt Nam"

    if query.get('keywords') is not None and len(query['keywords']) > 0:
        params['q'] = query['keywords']

    if query.get('location') is not None and len(query['location']) > 0:
        params['rbl'] = query['location']
        if params['rbl'] == 'Ho Chi Minh':
            params['rbl'] = 'Thành Phố Hồ Chí Minh'
            params['jlid']= 'b388d544e0e095c3'
        elif params['rbl'] == 'Ha Noi':
            params['rbl'] = 'Hà Nội'
            params['jlid']= '3f15a69abf4fcaff'

    if query.get('time') is not None and len(query['time']) > 0:
        params['fromage'] = query['time']
    
    if query.get('relevance') is not None and len(query['relevance']) > 0:
        params['sort'] = query['relevance']
        
    if query.get('type') is not None and len(query['type']) > 0:
        filters = ','.join(e for e in query['type'])
        params['jt'] = filters
    
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
        job_collection.insert_one({
                'title': job_dict['title'],
                'company': job_dict['company'],
                'location': job_dict['location'],
                'link': job_dict['link'],
                'job_description': job_dict.get('job_description', ""),
                'type': job_dict['query'].get('type',""),
                "time": job_dict['query'].get('time',""),
                "relevance": job_dict['query'].get('relevance',""),
                "keywords": job_dict['query'].get('keywords',"") })


def start_requests():
    s = HTMLSession()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for query in queries:
            start = 0
            br = False
            for i in range(config['num_pages']):
                if br:
                    break
                url = build_search_url(query)
                while True:
                    jobs = job_data_get(s, url)
                    if len(jobs[1]) == 0:
                        br = True
                        break
                    for job in jobs[1]:
                        futures.append(executor.submit(add_job_to_db, parse_html(s, job, query)))
                    try:
                        url = JOB_BASE_URL + jobs[0][0].attrs['href']
                    except IndexError as err:
                        print(err)
                        break
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")





def start_scaper(**kwargs):
    load_dotenv()
    global db, config, start, queries

    config = kwargs.get('config')
    queries = kwargs.get('queries')
    print(queries)
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client["Grab-Data"]
    start = 0# Start page
    
    start_requests()
        