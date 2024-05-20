from updatedb_gemini.py import process_job, process_cv
* process_job(job_dict) returns updated job_dict with industries and requirements keywords, call before adding job to database
* process_cv(cv_url) returns skills_dict containing all skill keywords extracted from cv, call after receiving cv from user