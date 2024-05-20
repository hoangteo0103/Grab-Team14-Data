from langchain_community.document_loaders import PyPDFLoader

def scan_pdf(url):
    loader = PyPDFLoader(url)
    pages = loader.load()
    content = ''
    for page in pages:
        content += page.page_content
    return content


def extract_info_by_cv(cv_url, chat):
    content = scan_pdf(cv_url)
    content = content.replace('\"', '\'')
    try:
        response = chat.send_message(f"You are doing keywords extracting task to preprocess data. Give me the skill keywords and information of job applicant from given resume content: ```{content}```. The answer must be in English.")
        fc = response.candidates[0].content.parts[0].function_call
        info = type(fc).to_dict(fc)["args"]
        info_dict = {'skills': []}
        for skill in ['technical_skills', 'soft_skills', 'additional_skills']:
            info_dict['skills'].extend(info[skill])

        info_dict['personal_information'] = info['personal_information']

        return info_dict
    except Exception as e:
        print(f"Error sending message: {e}")
        return {'skills': [], 'personal_information': {}}

