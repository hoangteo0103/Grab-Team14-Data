import os
from pymongo import MongoClient
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
from vertexai.preview.generative_models import ToolConfig

import scan_cv


vertexai.init(project=os.getenv('PROJECT_ID'), location=os.getenv('LOCATION'))


def gen_cover_letter(companyName, title, experience_level, requirement, job_desc, user_info):
    load_dotenv()
    vertexai.init(project=os.getenv('PROJECT_ID'), location=os.getenv('LOCATION'))

    model = GenerativeModel('gemini-1.5-pro-preview-0409',
                            generation_config=GenerationConfig(temperature=0)
                            )
    chat = model.start_chat()

    job_information = {}
    job_information["job_desc"] = job_desc
    job_information["company_name"] = companyName
    job_information["title"] = title
    job_information["experience_level"] = experience_level
    job_information["requirements"] = requirement

    try:
        response = chat.send_message(f"You are an assistant who help users to find jobs. Generate a cover letter given job information: {job_information}. given personal information: {user_info}. The answer must be in English. Skip any information that is not provided to make sure no masked token")
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Error sending message: {e}")
        return ''