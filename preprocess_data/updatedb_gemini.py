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




def process_job(job_dict):
    load_dotenv()
    vertexai.init(project=os.getenv('PROJECT_ID'), location=os.getenv('LOCATION'))
    job_desc = job_dict.get('description', "")

    extract_job_keywords_func = FunctionDeclaration(
        name="extract_job_keywords",
        description="Extract job information from a given job description.",
        parameters={
            "type": "object",
            "properties": {
                "industries": {
                    "type": "array",
                    "description": "A list of relevent industries",
                    "items": {
                        "description": "job industry",
                        "type": "string",
                    },
                },
                "requirements": {
                    "type": "array",
                    "description": "A list of position requirements",
                    "items": {
                        "description": "job requirement",
                        "type": "string",
                    },
                },
                # "responsibilities": {
                #     "type": "array",
                #     "description": "A list of position responsibilities",
                #     "items": {
                #         "description": "job responsibility",
                #         "type": "string",
                #     },
                # },
            },
            "required": ["industries", "requirements"],
        },
    )

    # Define a tool that includes the above functions
    job_tool = Tool(
        function_declarations=[extract_job_keywords_func],
    )

    # Define a tool config for the above functions
    job_tool_config = ToolConfig(
        function_calling_config=ToolConfig.FunctionCallingConfig(
            # ANY mode forces the model to predict a function call
            mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
            # List of functions that can be returned when the mode is ANY.
            # If the list is empty, any declared function can be returned.
            allowed_function_names=["extract_job_keywords"],
        )
    )

    model = GenerativeModel('gemini-1.5-pro-preview-0409',
                            generation_config=GenerationConfig(temperature=0),
                            tools=[job_tool],
                            tool_config=job_tool_config
                            )
    chat = model.start_chat()

    response = chat.send_message(f"Give me the industries, and requirements corresponding with the given JD: ```{job_desc}```")
    fc = response.candidates[0].content.parts[0].function_call
    info_dict = type(fc).to_dict(fc)["args"]

    # update job dict
    # job_dict["responsibilities"] = info_dict["responsibilities"]
    job_dict["requirements"] = info_dict["requirements"]
    job_dict["industries"] = info_dict["industries"]




def process_cv(cv_url):

    extract_skill_keywords_func = FunctionDeclaration(
    name="extract_skill_keywords",
    description="Extract skill keywords from a given resume.",
    parameters={
        "type": "object",
        "properties": {
            "technical_skills": {
                "type": "array",
                "description": "A list of technical skills",
                "items": {
                    "description": "technical skill keyword",
                    "type": "string",
                },
            },
            "soft_skills": {
                "type": "array",
                "description": "A list of soft skills",
                "items": {
                    "description": "soft skill keyword",
                    "type": "string",
                },
            },
            "additional_skills": {
                "type": "array",
                "description": "A list of additional skills",
                "items": {
                    "description": "additional skill keyword",
                    "type": "string",
                },
            },
        },
        "required": ["technical_skills", "soft_skills", "additional_skills"],
    },
    )

    # Define a tool that includes the above functions
    resume_tool = Tool(
        function_declarations=[extract_skill_keywords_func],
    )

    # Define a tool config for the above functions
    resume_tool_config = ToolConfig(
        function_calling_config=ToolConfig.FunctionCallingConfig(
            # ANY mode forces the model to predict a function call
            mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
            # List of functions that can be returned when the mode is ANY.
            # If the list is empty, any declared function can be returned.
            allowed_function_names=["extract_skill_keywords"],
        )
    )

    model = GenerativeModel('gemini-1.5-pro-preview-0409',
                            generation_config=GenerationConfig(temperature=0),
                            tools=[resume_tool],
                            tool_config=resume_tool_config
                            )
    chat = model.start_chat()

    skills_dict = scan_cv.extract_skill_by_cv(cv_url, chat)

    return skills_dict

