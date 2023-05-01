import docx2txt
import spacy
import re
import docx
import os
import time

def process_resumes(file_paths, requirements):
    start_time = time.time()
    print("Processing resumes:", file_paths)
    
    nlp = spacy.load("en_core_web_lg")

    phone_pattern = re.compile(r"\b\d{3}\D{0,3}\d{3}\D{0,3}\d{4}\b")
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")
    experience_pattern = re.compile(r'(\d+)\+?\s*(?:year|yr)s?\s+of\s+experience\s+in\s+(.*)', re.IGNORECASE)
    education_pattern = re.compile(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+))[\n\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+))(?:[\n\s]+[A-Z]{2}[\n\s]+)")
    language_pattern = re.compile(r'\b(?:English|French|German|Spanish|Italian|Portuguese|Russian|Chinese|Japanese|Korean|Vietnamese|Ukrainian|Uzbek|Turkish|Thai|Hindi|Greek|Georgain|Czech|Arabic)\b', re.IGNORECASE)
    job_title_pattern = r"\b(\w+\s)*(manager|director|engineer|analyst|specialist|consultant|coordinator)\b"

    
    reqs_list = requirements.split(",")
    reqs_list = [req.strip().replace('\xa0', ' ').lower() for req in reqs_list if req.strip()]


    skills_list = ['java', 'c++', 'javascript','php','ruby', 'html', 'css', 'react','sql', 'node', 'aws','web development','machine learning','artificial intelligence','composing','first aid',' use and disposal of chemicals', 'business consulting', 'teaching','math','project management', 'public speaking', 'accounting', 'python', 'communication', 'html5', 'MySQL', 'c#', 'singing', 'dancing', 'idol', 'arts']
    
    def extract_sec_info(resume_text, skills_list):
        doc = nlp(resume_text)
        name = None
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

        phone_number = None
        for match in re.findall(phone_pattern, resume_text):
            phone_number = match
            break

        email = None
        for match in re.findall(email_pattern, resume_text):
            email = match
            break
        
        return {
            "name": name,
            "phone_number": phone_number,
            "email": email,
            } 

    def extract_info(resume_text, skills_list):
        doc = nlp(resume_text)
        skills = []
        for skill in skills_list:
            if skill.lower() in resume_text.lower():
                skills.append(skill.lower())
        skills = list(set(skills))
       
        experience = []
        for match in experience_pattern.finditer(resume_text):
            years_of_experience = match.group(1)
            field = match.group(2)
            experience_str = f"{years_of_experience} years of experience in {field}"
            experience.append(experience_str.replace('\xa0', '').lower())


        job_titles = re.findall(job_title_pattern, resume_text, re.IGNORECASE)
        for title in job_titles:
            experience.append(''.join(filter(None, title)).lower())

        education = []
        for match in re.findall(education_pattern, resume_text):
            degree = match[0].lower()
            institution = match[1].lower()
            education.append(degree + ' ' + institution)

        if not education:
            lines = resume_text.split('\n')
            for line in lines:
                if 'degree' in line.lower() or 'bachelor' in line.lower() or 'master' in line.lower():
                    education.append(line.strip().lower())
        
        languages = []       
        for match in re.findall(language_pattern, resume_text):
            languages.append(match.lower())
        
        my_list=[]
        my_list.extend(skills)
        my_list.extend(experience)
        my_list.extend(education)
        my_list.extend(languages)
        
        return my_list
    import math
    from collections import Counter

    def cosine_similarity(info,reqs_list):
        l1=[]; l2=[]
        rvector = info +reqs_list
        for word in rvector:
            if word in info: l1.append(1) 
            else: l1.append(0)
            if word in reqs_list: l2.append(1)
            else: l2.append(0)
        c = 0

        for i in range(len(rvector)):
            c+= l1[i]*l2[i]
        cosine = c / float((sum(l1)*sum(l2))**0.5)
        return cosine*100 

    
    resume_scores = {}
    for file_path in file_paths:
        print("Processing file:", file_path)
        file_name = os.path.basename(file_path)
        resume_text = docx2txt.process(file_path)
        info = extract_info(resume_text, skills_list)
        sec_info = extract_sec_info(resume_text, skills_list)
        cosine = cosine_similarity(info, reqs_list)
        resume_scores[file_name] = {
            "cosine": cosine,
            "sec_info": sec_info
        }
        print("Processed:", file_name, cosine, sec_info)

    top_scores = [0.0] * 3
    top_files = [[] for _ in range(3)]

    if len(resume_scores) < 3:
        print(f"Be careful !!! There are only {len(resume_scores)} resumes.")

    for file, score_data in resume_scores.items():
        score = score_data["cosine"]
        if score > top_scores[0]:
            top_scores = [score, top_scores[0], top_scores[1]]
            top_files = [[file], top_files[0], top_files[1]]
        elif score > top_scores[1]:
            top_scores = [top_scores[0], score, top_scores[1]]
            top_files = [top_files[0], [file], top_files[1]]
        elif score > top_scores[2]:
            top_scores = [top_scores[0], top_scores[1], score]
            top_files = [top_files[0], top_files[1], [file]]
        elif score == top_scores[0]:
            top_files[0].append(file)
        elif score == top_scores[1]:
            top_files[1].append(file)
        elif score == top_scores[2]:
            top_files[2].append(file)

    for i, (score, files) in enumerate(zip(top_scores, top_files)):
        updated_files = []  
        for file_name in files:
            resume = resume_scores[os.path.basename(file_name)]  

            resume_info = {
                "filename": file_name,
                "score": resume["cosine"],
                "name": resume["sec_info"]["name"],
                "phone_number": resume["sec_info"]["phone_number"],
                "email": resume["sec_info"]["email"]
            }
            updated_files.append(resume_info)  
        top_files[i] = updated_files  

    return top_files


    
