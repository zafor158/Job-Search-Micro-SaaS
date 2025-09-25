def optimize_keywords(profile: dict) -> dict:
    """
    Optimizes the skills section for ATS by adding and capitalizing relevant keywords.
    Handles skills as a single string (from form) or a list (from LLM).
    """
    keywords = [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust", "PHP",
        "Machine Learning", "Data Analysis", "Data Science", "Deep Learning", "NLP", "AI",
        "Project Management", "Agile", "Scrum", "Product Management",
        "SQL", "NoSQL", "PostgreSQL", "MongoDB", "MySQL", "Big Data",
        "AWS", "Azure", "Google Cloud Platform (GCP)", "Cloud Computing", "Terraform",
        "API Design", "RESTful APIs", "Microservices", "GraphQL",
        "Docker", "Kubernetes", "CI/CD", "Jenkins", "Git", "DevOps"
    ]
    
    skills_data = profile.get("skills")

    if isinstance(skills_data, str):
        skills_text = skills_data
        skills_text_lower = skills_text.lower()
        for kw in keywords:
            if kw.lower() in skills_text_lower and kw not in skills_text:
                skills_text += f", {kw}"
        profile["skills"] = skills_text
    
    elif isinstance(skills_data, list):
        skills_list = skills_data
        skills_list_lower = [s.lower() for s in skills_list]
        for kw in keywords:
            if kw.lower() in skills_list_lower and kw not in skills_list:
                skills_list.append(kw)
        profile["skills"] = skills_list
        
    return profile

