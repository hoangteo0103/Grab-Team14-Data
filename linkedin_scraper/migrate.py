from setup import setup
db, queries, config = setup()
print(db['jobs_linkedin_old'].count_documents({}))
for job in db['jobs_linkedin_old'].find():
    if db['jobs'].find_one({'jobLink': job['job_url'], }):
        oldJob = db['jobs'].find_one({'jobLink': job['job_url'], })
        oldJob['description'] = job['job_description']
        oldJob['date'] = job['date']
        oldJob['companyLink'] = job['company_link']
        db['jobs'].update_one({'jobLink': job['job_url']}, {'$set': oldJob})
        continue

    db['jobs'].insert_one({
        'title': job['title'],
        'company': job['company'],
        'date': job['date'],
        'location': job.get('location', ""),
        'companyLocation': job.get('company_location', ""),
        'jobLink': job['job_url'],
        'description': job.get('job_description', ""),
        'companyImageUrl' : job.get('company_image_url', "https://images.rawpixel.com/image_png_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvdjk4Mi1kMy0xMC5wbmc.png"),
        'companyLink': job.get('company_link', ""),
        'platform': 'Linkedin'

    })