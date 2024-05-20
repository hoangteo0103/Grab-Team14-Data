from setup import setup
db, queries, config = setup()
print(db['job_indeed'].count_documents({}))
for job in db['job_indeed'].find():
    location = job['location']
    if location[0] == 'T':
        location = 'Ho Chi Minh'
    else :
        location = 'Ha Noi'
    
    if db['jobs'].find_one({'jobLink': job['link'], }):
        continue
    db['jobs'].insert_one({
        'title': job['title'],
        'company': job['company'],
        'location': location,
        'companyLocation': job.get('location', ""),
        'jobLink': job['link'],
        'description': job.get('job_description', ""),
        'companyImageUrl' : job.get('company_image_url', "https://logos-world.net/wp-content/uploads/2021/02/Indeed-Symbol.png"),
        'companyLink': job.get('company_link', ""),
        'platform': 'Indeed',
        'requirements': job.get('requirements', ""),
        'industries': job.get('industries', ""),

    })