#updated version for both manual form input and PDF upload
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_resume_json(request_data: dict) -> dict:
    """
    Generates resume content as a JSON object.
    This function handles two scenarios:
    1. A structured user profile from a form.
    2. Extracted text from a PDF with modification instructions.
    """
    
    # --- Check which scenario we are handling ---
    if 'extracted_text' in request_data:
        # SCENARIO 2: PDF Upload with modification instructions
        extracted_text = request_data.get('extracted_text')
        instructions = request_data.get('modification_instructions', {})
        
        job_title = instructions.get('jobTitle', 'the target role')
        key_skills = instructions.get('keySkills', 'relevant skills')
        tone = instructions.get('tone', 'professional')

        system_prompt = f"""
        You are an expert career coach. Your task is to rewrite and enhance a resume based on the user's raw text and specific instructions.

        **Instructions:**
        1.  Analyze the original resume text provided by the user.
        2.  Rewrite and tailor it specifically for the job title: **{job_title}**.
        3.  Emphasize and integrate these key skills throughout the experience section: **{key_skills}**.
        4.  Adopt a **{tone}** tone in all written content.
        5.  Extract the user's name, email, and phone number from the text. If they are not present, use placeholders.
        6.  Return the output as a single, clean JSON object with keys: "name", "email", "phone", "summary", "experience" (a list of objects with "title", "company", "dates", and "bullets" keys), "education", and "skills" (a list of strings).
        """
        user_content = f"Here is the original resume text to rewrite:\n\n<resume_text>\n{extracted_text}\n</resume_text>"

    else:
        # SCENARIO 1: Structured user profile from a form
        profile_str = "\n".join([f"{k}: {v}" for k, v in request_data.items()])

        system_prompt = (
            "You are a professional resume writer. Based on the user's profile, generate a compelling summary, "
            "rewrite their experience bullet points to be action-oriented, and list their key skills. "
            "Return the output as a single, clean JSON object with keys: 'summary', 'experience' (a list of objects "
            "with 'title', 'company', 'dates', and 'bullets' keys), and 'skills' (a list of strings). "
            "Optimize the content with industry keywords for technical roles."
        )
        user_content = f"Create resume content using this profile:\n{profile_str}"

    # --- Common logic for calling the LLM and parsing the response ---
    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # Use a powerful Groq model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object"}  # Enforce JSON output
    )

    try:
        content = chat_completion.choices[0].message.content
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise Exception(f"Failed to parse LLM response: {e}")


#new version
# import os
# import json
# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()
# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# def generate_resume_json(profile: dict) -> dict:
#     """
#     Generates resume content as a JSON object using Groq LLM.
#     """
#     profile_str = "\n".join([f"{k}: {v}" for k, v in profile.items()])

#     system_prompt = (
#         "You are a professional resume writer. Based on the user's profile, generate a compelling summary, "
#         "rewrite their experience bullet points to be action-oriented, and list their key skills. "
#         "Return the output as a single, clean JSON object with keys: 'summary', 'experience' (a list of objects "
#         "with 'title', 'company', 'dates', and 'bullets' keys), and 'skills' (a list of strings). "
#         "Optimize the content with industry keywords for technical roles."
#     )

#     chat_completion = client.chat.completions.create(
#          model="openai/gpt-oss-20b", # A powerful model for structured data
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"Create resume content using this profile:\n{profile_str}"}
#         ],
#         response_format={"type": "json_object"} # Enforce JSON output
#     )

#     try:
#         content = chat_completion.choices[0].message.content
#         return json.loads(content)
#     except (json.JSONDecodeError, KeyError, IndexError) as e:
#         raise Exception(f"Failed to parse LLM response: {e}")

# old version    
# import os
# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()

# # Initialize Groq client
# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# def generate_resume(profile: dict) -> str:
#     """
#     Generates an ATS-friendly resume in HTML format using Groq LLM.
#     :param profile: dict containing user profile info (name, skills, experience, education, etc.)
#     :return: str containing HTML resume
#     """

#     # Convert profile dict to formatted string
#     profile_str = "\n".join([f"{k}: {v}" for k, v in profile.items()])

#     # System prompt to guide the LLM for ATS-friendly HTML resume
#     system_prompt = (
#         "You are a professional resume writer. "
#         "Generate a clean, ATS-friendly resume in HTML format. "
#         "Include these sections: Name, Contact, Summary, Experience, Education, Skills. "
#         "Optimize with industry keywords for technical roles. "
#         "Use simple HTML, avoid complex CSS or scripts. "
#         "Ensure it is readable by applicant tracking systems."
#     )

#     # Create chat completion
#     chat_completion = client.chat.completions.create(
#         model="openai/gpt-oss-20b",  # choose appropriate Groq model
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"Create a resume using this profile:\n{profile_str}"}
#         ],
#         stream=False
#     )

#     # Extract generated HTML from response
#     try:
#         resume_html = chat_completion.choices[0].message.content
#     except (KeyError, IndexError):
#         raise Exception(f"Unexpected LLM response format: {chat_completion}")

#     return resume_html