from requests_html import HTMLSession
import concurrent.futures
from bs4 import BeautifulSoup
from constants import *

from pymongo import MongoClient
import os
from urllib.parse import urlparse, urlencode
from dotenv import load_dotenv
from logger import debug
from preprocess_data.updatedb_gemini import process_job

def job_data_get(s, url: str) -> tuple:
    # return the elements for each job card
    r = s.get(url)
    return r.html.find('ul.pagination-list a[aria-label=Next]'), r.html.find('div.job_seen_beacon')

def parse_html_job_desc(s, job_dict) -> dict:
    job_desc_req = s.get(job_dict['jobLink'])
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


    img = job_desc_soup.find('img', class_='jobsearch-JobInfoHeader-logo')
    if img:
        job_dict['companyImageUrl'] = img.attrs['src']
    else:
        job_dict['companyImageUrl'] = 'https://logos-world.net/wp-content/uploads/2021/02/Indeed-Symbol.png'

    div = job_desc_soup.find('div', class_='jobsearch-JobInfoHeader-title-container')

    if div:
        cmp_link = div.find('a')
        job_dict['companyLink'] = cmp_link.attrs['href'] if cmp_link else ''
    return job_dict

def parse_html(s, job, query) -> dict:
    soup = BeautifulSoup(job.html, 'html.parser')

    companyname = soup.find('span', attrs={'data-testid': 'company-name'})
    companylocation = soup.find('div', attrs={'data-testid': 'text-location'})
    job_dict = {'title': job.find('h2 > a')[0].text,
                'jobLink': 'https://vn.indeed.com/viewjob?jk=' + job.find('h2 > a')[0].attrs['data-jk'] if job.find('h2 > a') else 'no link',
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
        if query.get('time') == 'DAY':
            params['fromage'] = '1'
        if query.get('time') == 'WEEK':
            params['fromage'] = '7'
        if query.get('time') == 'MONTH':
            params['fromage'] = '30'
    
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
    job_collection = db["job_indeed"]
    print(job_dict)
    if job_collection.find_one({'jobLink': job_dict['jobLink'], }):
        job  = job_collection.find_one({'jobLink': job_dict['jobLink']})
        if 'industry' in job_dict['query']:
            for code in job_dict['query']['industry']:
                if code not in job['industry']:
                    job['industry'].append(code)
        
        if 'type' not in job and 'type' in job_dict['query']:
            job['type'] = job_dict['query']['type']

        if 'experience' not in job and 'experience' in job_dict['query']:
            job['experience'] = job_dict['query']['experience']

        if 'workingMode' not in job and 'workingMode' in job_dict:
            job['workingMode'] = job_dict['workingMode']
        
        if 'description' in job and len(job['description']) == 0 or 'description' not in job:
            job['description'] = job_dict['description']

        if 'companyImageUrl' in job and len(job['companyImageUrl']) == 0 or 'companyImageUrl' not in job:
            job['companyImageUrl'] = job_dict['companyImageUrl']

        if 'companyLink' in job and len(job['companyLink']) == 0 or 'companyLink' not in job:
            job['companyLink'] = job_dict['companyLink']
        job_collection.update_one({'jobLink': job_dict['jobLink'], 'company': job_dict['company'], 'title': job_dict['title']}, {'$set': job})
    else:
        job_dict = process_job(job_dict)
        print(job_dict)
        return 
        job_collection.insert_one({
                'title': job_dict['title'],
                'company': job_dict['company'],
                'location': job_dict['location'],
                'jobLink': job_dict['jobLink'],
                'description': job_dict.get('description', ""),
                'type': job_dict['query'].get('type',""),
                "time": job_dict['query'].get('time',""),
                'companyImageUrl' : job_dict.get('companyImageUrl', ""),
                'companyLink': job_dict.get('companyLink', ""),
                'platform': 'Indeed',
                'requirements': job_dict.get('requirements', ""),
                'industry': job_dict.get('industry', ""),
                }
        )


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
                print(url)
                while True:
                    jobs = job_data_get(s, url)
                    print(jobs)
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
    print("TFF")
    global db, config, start, queries

    config = kwargs.get('config')
    queries = kwargs.get('queries')
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client["Grab-Data"]
    start = 0# Start page
    
    start_requests()
        