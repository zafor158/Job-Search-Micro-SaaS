# services.py
import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict

load_dotenv()

# --- INITIALIZE CLIENTS AND MODELS ---
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    print("Warning: GROQ_API_KEY not found in environment variables.")
    print("AI features will not work without a valid GROQ API key.")
    print("Please set GROQ_API_KEY in your .env file or environment variables.")
    client = None
else:
    client = Groq(api_key=groq_api_key)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- RESUME & COVER LETTER SERVICES (WITH FIXED PROMPT) ---

# In services.py

def generate_resume_json(request_data: dict) -> dict:
    """
    Generates resume content as a JSON object.
    This function handles two scenarios:
    1. A structured user profile from a form.
    2. Extracted text from a PDF with modification instructions.
    """
    
    # Validate input data
    if not request_data or not isinstance(request_data, dict):
        raise ValueError("Invalid request data: must be a non-empty dictionary")
    
    # Check if GROQ client is available
    if client is None:
        print("Warning: GROQ API not available, using template-based resume generation")
        return generate_template_resume(request_data)
    
    if 'extracted_text' in request_data:
        # SCENARIO 2: PDF Upload
        extracted_text = request_data.get('extracted_text')
        instructions = request_data.get('modification_instructions', {})
        job_title = instructions.get('jobTitle', 'the target role')
        key_skills_list = instructions.get('keySkills', [])
        key_skills_str = ", ".join(key_skills_list)
        tone = instructions.get('tone', 'professional')

        system_prompt = f"""
        You are a world-class career coach. Your task is to rewrite a resume from raw text based on specific tailoring instructions.

        **Instructions:**
        1. Analyze the original resume text.
        2. Rewrite and tailor it for the job title: **{job_title}**.
        3. Strategically emphasize these key skills: **{key_skills_str}**.
        4. Adopt a **{tone}** and action-oriented tone.
        5. Return a single, clean JSON object.
        
        **CRITICAL JSON FORMATTING RULES:**
        - The JSON MUST have these exact top-level keys: "name", "email", "phone", "summary", "experience", "projects", "education", and "skills".
        - The "experience" key MUST be a list of objects, each with "title", "company", "dates", and "bullets" (a list of strings).
        - The "projects" key MUST be a list of objects. Each object MUST have ONLY two keys: "title" (a string) and "bullets" (a list of strings).
        - **The "education" key MUST be a single flat string, not an object or a list. Summarize all education details into one line.** # <-- NEW EXPLICIT RULE
        - The "skills" key MUST be a simple list of strings.
        - Use placeholders like "N/A" if any information is missing.
        """
        user_content = f"Here is the original resume text to rewrite:\n\n<resume_text>\n{extracted_text}\n</resume_text>"

    else:
        # SCENARIO 1: Structured user profile from a form
        profile = request_data
        system_prompt = (
            "You are an expert resume writer. Based on the user's raw profile data, generate the core components of a polished resume. "
            "**Your tasks are to:**\n"
            "1. Extract and format the user's name, email, and phone from the profile data.\n"
            "2. Write a compelling professional summary (2-3 sentences).\n"
            "3. Rewrite the experience bullet points to be action-oriented and quantified (STAR method).\n"
            "4. Parse the projects into structured data, rewriting descriptions into bullet points.\n"
            "5. Parse the skills into a clean list of relevant skills.\n"
            "6. Return a single, clean JSON object.\n\n"
            "**CRITICAL JSON FORMATTING RULES:**\n"
            "- The JSON MUST have these exact keys: 'name', 'email', 'phone', 'summary', 'experience', 'projects', 'education', and 'skills'.\n"
            "- The 'name' key MUST be a string with the user's full name.\n"
            "- The 'email' key MUST be a string with the user's email address.\n"
            "- The 'phone' key MUST be a string with the user's phone number.\n"
            "- The 'experience' key MUST be a list of objects, each with 'title', 'company', 'dates', and 'bullets' (a list of strings).\n"
            "- The 'projects' key MUST be a list of objects. Each object MUST have ONLY two keys: 'title' (a string) and 'bullets' (a list of strings). Convert any project descriptions into 1-2 bullet points.\n"
            "- The 'education' key MUST be a single flat string. Use 'N/A' if no education information is provided.\n"
            "- The 'skills' key MUST be a simple list of strings.\n"
            "- Use placeholders like 'N/A' if any information is missing."
        )
        llm_input_data = {k: profile[k] for k in ['name', 'email', 'phone', 'summary', 'experience', 'projects', 'skills'] if profile.get(k)}
        user_content = f"Create resume content using this profile data:\n{json.dumps(llm_input_data)}"
    
    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )

        content = chat_completion.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        if "invalid_api_key" in str(e) or "AuthenticationError" in str(e):
            print("Warning: GROQ API key is invalid or expired, using template-based resume generation")
            return generate_template_resume(request_data)
        elif "rate_limit" in str(e).lower():
            print("Warning: GROQ API rate limit exceeded, using template-based resume generation")
            return generate_template_resume(request_data)
        else:
            print(f"Warning: GROQ API error ({str(e)}), using template-based resume generation")
            return generate_template_resume(request_data)
# (The rest of the services.py file can remain the same)
def generate_cover_letter_text(request_data: dict) -> str:
    # Validate input data
    if not request_data or not isinstance(request_data, dict):
        raise ValueError("Invalid request data: must be a non-empty dictionary")
    
    # Check if GROQ client is available
    if client is None:
        print("Warning: GROQ API not available, using template-based cover letter generation")
        return generate_template_cover_letter(request_data)
    
    profile = request_data.get('user_profile', {})
    job_description = request_data.get('job_description', '')
    company_name = request_data.get('company_name', 'the company')
    hiring_manager = request_data.get('hiring_manager', '')
    personal_note = request_data.get('personal_note', '')

    # Ensure profile is a dictionary and filter out None/empty values
    if not isinstance(profile, dict):
        profile = {}
    
    profile_str = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in profile.items() if v and k])

    system_prompt = f"""
    You are a professional career writer crafting compelling cover letters.

    **Instructions:**
    1.  Address the letter to "{hiring_manager if hiring_manager else 'the Hiring Team'}".
    2.  State the position and express specific enthusiasm for **{company_name}**.
    3.  Connect the user's most relevant experiences to 2-3 key requirements from the job description.
    4.  Seamlessly integrate this personal note: "{personal_note}"
    5.  Include a confident call to action.
    6.  Return only the raw text of the cover letter.
    """

    user_content = f"**User Profile:**\n{profile_str}\n\n**Job Description:**\n{job_description}"
    
    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        if "invalid_api_key" in str(e) or "AuthenticationError" in str(e):
            print("Warning: GROQ API key is invalid or expired, using template-based cover letter generation")
            return generate_template_cover_letter(request_data)
        elif "rate_limit" in str(e).lower():
            print("Warning: GROQ API rate limit exceeded, using template-based cover letter generation")
            return generate_template_cover_letter(request_data)
        else:
            print(f"Warning: GROQ API error ({str(e)}), using template-based cover letter generation")
            return generate_template_cover_letter(request_data)

def fetch_adzuna_jobs(query: str, location: str, country_code: str = 'gb') -> List[Dict]:
    """Fetches job listings from the Adzuna API."""
    ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
    ADZUNA_API_KEY = os.environ.get("ADZUNA_API_KEY")
    if not all([ADZUNA_APP_ID, ADZUNA_API_KEY]):
        print("Warning: Adzuna API credentials not found in .env file. Skipping Adzuna.")
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        'app_id': ADZUNA_APP_ID, 'app_key': ADZUNA_API_KEY,
        'results_per_page': 50, 'what': query, 'where': location,
        'content-type': 'application/json'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        jobs = []
        for result in data.get('results', []):
            jobs.append({
                'title': result.get('title'),
                'company': result.get('company', {}).get('display_name', 'N/A'),
                'location': result.get('location', {}).get('display_name', 'N/A'),
                'description': result.get('description', 'No description available.'),
                'url': result.get('redirect_url')
            })
        return jobs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs from Adzuna: {e}")
        print("This might be due to: 1) Missing/invalid API credentials, 2) Rate limiting, 3) Network issues")
        return []

def fetch_jsearch_jobs(query: str, location: str) -> List[Dict]:
    """(NEW) Fetches job listings from the JSearch API."""
    JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY")
    if not JSEARCH_API_KEY:
        print("Warning: JSearch API key not found in .env file. Skipping JSearch.")
        return []
        
    url = "https://jsearch.p.rapidapi.com/search"
    params = {"query": f"{query} in {location}", "num_pages": "1"}
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        jobs = []
        for result in data.get('data', []):
            jobs.append({
                'title': result.get('job_title'),
                'company': result.get('employer_name', 'N/A'),
                'location': result.get('job_city', 'N/A') + ", " + result.get('job_country', 'N/A'),
                'description': result.get('job_description', 'No description available.'),
                'url': result.get('job_apply_link', '#')
            })
        return jobs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs from JSearch: {e}")
        print("This might be due to: 1) Missing/invalid API key, 2) Inactive subscription, 3) Rate limiting")
        return []

def fetch_all_jobs(query: str, location: str, country_code: str = 'gb') -> List[Dict]:
    """(NEW) Fetches from all job portals, combines, and removes duplicates."""
    adzuna_jobs = fetch_adzuna_jobs(query, location, country_code)
    jsearch_jobs = fetch_jsearch_jobs(query, location)
    
    all_jobs = adzuna_jobs + jsearch_jobs
    
    # Simple deduplication based on title and company
    unique_jobs = []
    seen = set()
    for job in all_jobs:
        # Ensure job title and company are strings before calling .lower()
        title = job.get('title') or ''
        company = job.get('company') or ''
        identifier = (title.lower(), company.lower())
        if identifier not in seen:
            unique_jobs.append(job)
            seen.add(identifier)
            
    print(f"Found {len(adzuna_jobs)} jobs from Adzuna, {len(jsearch_jobs)} from JSearch. Total unique jobs: {len(unique_jobs)}")
    
    # If no jobs found, provide helpful message
    if len(unique_jobs) == 0:
        print("No jobs found. This might be due to:")
        print("1. Missing API keys in .env file")
        print("2. API rate limits exceeded")
        print("3. Network connectivity issues")
        print("4. No jobs available for the search criteria")
    
    return unique_jobs

def calculate_job_scores(user_profile_text: str, jobs: list) -> list:
    if not jobs or not user_profile_text:
        return []
    user_embedding = embedding_model.encode(user_profile_text, convert_to_tensor=True)
    job_descriptions = [job.get('description', '') for job in jobs]
    job_embeddings = embedding_model.encode(job_descriptions, convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, job_embeddings)
    for i, job in enumerate(jobs):
        job['score'] = round(float(cosine_scores[0][i]), 4)
    return jobs

def rank_jobs(scored_jobs: list, top_n: int = 10) -> list:
    ranked = sorted(scored_jobs, key=lambda j: j.get('score', 0), reverse=True)
    return ranked[:top_n]

def generate_template_resume(request_data: dict) -> dict:
    """
    Fallback template-based resume generation when AI services are not available.
    """
    if 'extracted_text' in request_data:
        # For PDF uploads, return a basic structure
        return {
            "name": "Your Name",
            "email": "your.email@example.com",
            "phone": "Your Phone Number",
            "summary": "Professional summary based on your experience and skills.",
            "experience": [
                {
                    "title": "Job Title",
                    "company": "Company Name",
                    "dates": "Start Date - End Date",
                    "bullets": ["Key achievement 1", "Key achievement 2", "Key achievement 3"]
                }
            ],
            "projects": [
                {
                    "title": "Project Name",
                    "bullets": ["Project description 1", "Project description 2"]
                }
            ],
            "education": "Your educational background",
            "skills": ["Skill 1", "Skill 2", "Skill 3"]
        }
    else:
        # For structured data, format it properly
        profile = request_data
        
        # Format experience
        experience = []
        if isinstance(profile.get('experience'), list):
            for exp in profile['experience']:
                if isinstance(exp, dict):
                    experience.append({
                        "title": exp.get('title', 'Job Title'),
                        "company": exp.get('company', 'Company Name'),
                        "dates": exp.get('dates', 'Start Date - End Date'),
                        "bullets": exp.get('bullets', []) if isinstance(exp.get('bullets'), list) else []
                    })
        
        # Format projects
        projects = []
        if isinstance(profile.get('projects'), list):
            for proj in profile['projects']:
                if isinstance(proj, dict):
                    projects.append({
                        "title": proj.get('title', 'Project Name'),
                        "bullets": proj.get('bullets', []) if isinstance(proj.get('bullets'), list) else []
                    })
        
        # Format skills
        skills = []
        if isinstance(profile.get('skills'), list):
            skills = profile['skills']
        
        return {
            "name": profile.get('name', 'Your Name'),
            "email": profile.get('email', 'your.email@example.com'),
            "phone": profile.get('phone', 'Your Phone Number'),
            "summary": profile.get('summary', 'Professional summary highlighting your key strengths and experience.'),
            "experience": experience,
            "projects": projects,
            "education": profile.get('education', 'Your educational background'),
            "skills": skills
        }

def generate_template_cover_letter(request_data: dict) -> str:
    """
    Fallback template-based cover letter generation when AI services are not available.
    """
    profile = request_data.get('user_profile', {})
    job_description = request_data.get('job_description', '')
    company_name = request_data.get('company_name', 'the company')
    hiring_manager = request_data.get('hiring_manager', '')
    personal_note = request_data.get('personal_note', '')
    
    name = profile.get('name', 'Your Name')
    email = profile.get('email', 'your.email@example.com')
    phone = profile.get('phone', 'Your Phone Number')
    
    greeting = f"Dear {hiring_manager}," if hiring_manager else "Dear Hiring Manager,"
    
    cover_letter = f"""{greeting}

I am writing to express my strong interest in the position at {company_name}. With my background and skills, I am confident that I would be a valuable addition to your team.

{f"Personal Note: {personal_note}" if personal_note else ""}

Based on the job requirements, I believe my experience aligns well with what you are looking for. I am excited about the opportunity to contribute to {company_name} and would welcome the chance to discuss how my skills and experience can benefit your organization.

Thank you for considering my application. I look forward to hearing from you soon.

Sincerely,
{name}
{email}
{phone}"""
    
    return cover_letter


