from langchain_community.document_loaders import PyPDFLoader

def scan_pdf(url):
    loader = PyPDFLoader(url)
    pages = loader.load()
    content = ''
    for page in pages:
        content += page.page_content
    return content


def extract_skill_by_cv(cv_url, chat):
    content = scan_pdf(cv_url)
    try:
        response = chat.send_message(f"Give me skill keywords from given resume content: ```{content}```")
        fc = response.candidates[0].content.parts[0].function_call
        skills = type(fc).to_dict(fc)["args"]
        skills_dict = {'skills': []}
        for skill in skills:
            skills_dict['skills'].extend(skills[skill])

        return skills_dict
    except Exception as e:
        print(f"Error sending message: {e}")
        return {'skills': []}

