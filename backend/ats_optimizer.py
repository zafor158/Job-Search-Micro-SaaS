# updated version for both to handle manual input and uploaded pdf

def optimize_keywords(profile: dict) -> dict:
    """
    Optimizes the skills section for ATS by ensuring proper capitalization and adding relevant keywords.
    This function handles two types of input for skills:
    1. A single string (from a form).
    2. A list of strings (from an LLM response).
    """
    # A standard list of high-value keywords to check for
    keywords = [
        "Python", "Java", "C++", "JavaScript", "Go", "Rust",
        "Machine Learning", "Data Analysis", "Deep Learning", "NLP",
        "Project Management", "Agile", "Scrum",
        "SQL", "NoSQL", "PostgreSQL", "MongoDB",
        "AWS", "Azure", "Google Cloud", "Cloud Computing",
        "API", "RESTful APIs", "Microservices",
        "Docker", "Kubernetes", "CI/CD"
    ]
    
    skills_data = profile.get("skills")

    # --- SCENARIO 1: Skills data is a single string (from manual form input) ---
    if isinstance(skills_data, str):
        skills_text = skills_data
        for kw in keywords:
            # If a keyword is mentioned (case-insensitive) but not properly capitalized, add it.
            if kw.lower() in skills_text.lower() and kw not in skills_text:
                skills_text += f", {kw}"
        
        profile["skills"] = skills_text
        return profile

    # --- SCENARIO 2: Skills data is a list of strings (from PDF/LLM workflow) ---
    elif isinstance(skills_data, list):
        skills_list = skills_data
        # Create a lowercase version for easy, case-insensitive searching
        skills_list_lower = [s.lower() for s in skills_list]
        
        for kw in keywords:
            # If a keyword is mentioned but not properly capitalized, add it to the list
            if kw.lower() in skills_list_lower and kw not in skills_list:
                skills_list.append(kw)
        
        profile["skills"] = skills_list
        return profile

    # --- Fallback: If skills are missing or in an unknown format, do nothing ---
    else:
        return profile






#old version
# def optimize_keywords(profile: dict) -> dict:
#     """
#     Simple ATS optimization: emphasize skills and industry keywords.
#     """
#     keywords = ["Python", "Java", "C++", "Machine Learning", "Data Analysis", 
#                 "Project Management", "SQL", "AWS", "Cloud", "API"]
    
#     skills_text = profile.get("skills", "")
#     for kw in keywords:
#         if kw.lower() in skills_text.lower() and kw not in skills_text:
#             skills_text += f", {kw}"
    
#     profile["skills"] = skills_text
#     return profile
