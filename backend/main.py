#updated version for uploaded pdf resume modification
import fitz  # PyMuPDF
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from fastapi.responses import Response

# Import the single, unified function from resume_llm
from backend.resume_llm import generate_resume_json
# We'll re-add the optimizer for the manual workflow
from backend.ats_optimizer import optimize_keywords

import uvicorn

app = FastAPI(title="ATS Resume Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# --- Pydantic Models ---
class UserProfile(BaseModel):
    name: str
    email: str
    phone: str
    experience: str
    skills: str
    education: str
    additional_info: str = ""

class ModificationRequest(BaseModel):
    extracted_text: str
    modification_instructions: dict

class Experience(BaseModel):
    title: str
    company: str
    dates: str
    bullets: List[str]

class FinalResume(BaseModel):
    name: str
    email: str
    phone: str
    summary: str
    experience: List[Experience]
    skills: List[str]
    education: str

# --- API Endpoints ---

# ENDPOINT FOR MANUAL FORM (This was missing)
@app.post("/generate_resume")
async def create_resume_from_form(profile: UserProfile):
    try:
        optimized_profile = optimize_keywords(profile.dict())
        # The unified function handles the dictionary from the form
        resume_json = generate_resume_json(optimized_profile)
        
        # Combine original info with generated content for consistency
        full_resume_data = {
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "education": profile.education,
            **resume_json
        }
        return full_resume_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS FOR PDF WORKFLOW (These are correct)
@app.post("/upload/pdf")
async def upload_and_parse_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        pdf_bytes = await file.read()
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            extracted_text = "".join(page.get_text() for page in doc)
        return {"extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")

@app.post("/generate_modified_resume")
async def create_modified_resume(request: ModificationRequest):
    try:
        # The unified function handles the modification request
        resume_json = generate_resume_json(request.dict())
        return resume_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/pdf")
async def export_resume_as_pdf(resume_data: FinalResume):
    try:
        env = Environment(loader=FileSystemLoader('backend'))
        template = env.get_template("resume_template.html")
        html_content = template.render(resume_data.dict())
        pdf_bytes = HTML(string=html_content).write_pdf()
        return Response(
            content=pdf_bytes, media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Generated_Resume.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)





#new version
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML
# from fastapi.responses import Response

# # Assuming your functions are in a 'backend' folder
# from backend.resume_llm import generate_resume_json
# from backend.ats_optimizer import optimize_keywords

# import uvicorn

# app = FastAPI(title="ATS Resume Generator")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# )

# # --- Pydantic Models ---
# class UserProfile(BaseModel):
#     name: str
#     email: str
#     phone: str
#     experience: str
#     skills: str
#     education: str
#     additional_info: str = ""

# class Experience(BaseModel):
#     title: str
#     company: str
#     dates: str
#     bullets: List[str]

# class FinalResume(BaseModel):
#     name: str
#     email: str
#     phone: str
#     summary: str
#     experience: List[Experience]
#     skills: List[str]
#     education: str

# # --- API Endpoints ---
# @app.post("/generate_resume")
# async def create_resume_content(profile: UserProfile):
#     try:
#         optimized_profile = optimize_keywords(profile.dict())
#         resume_json = generate_resume_json(optimized_profile)
#         # Combine original profile info with generated content
#         full_resume_data = {
#             "name": profile.name,
#             "email": profile.email,
#             "phone": profile.phone,
#             "education": profile.education,
#             **resume_json
#         }
#         return full_resume_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/export/pdf")
# async def export_resume_as_pdf(resume_data: FinalResume):
#     try:
#         env = Environment(loader=FileSystemLoader('backend')) # Look for templates in the backend folder
#         template = env.get_template("resume_template.html")
#         html_content = template.render(resume_data.dict())
#         pdf_bytes = HTML(string=html_content).write_pdf()
#         return Response(
#             content=pdf_bytes,
#             media_type="application/pdf",
#             headers={"Content-Disposition": "attachment; filename=Generated_Resume.pdf"}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)






# previous version
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from backend.resume_llm import generate_resume
# from backend.ats_optimizer import optimize_keywords

# import uvicorn

# app = FastAPI(title="ATS Resume Generator Prototype")

# # Allow frontend requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # User profile model
# class UserProfile(BaseModel):
#     name: str
#     email: str
#     phone: str
#     experience: str
#     skills: str
#     education: str
#     additional_info: str = ""

# @app.post("/generate_resume")
# async def create_resume(profile: UserProfile):
#     try:
#         # Optimize keywords for ATS
#         optimized_profile = optimize_keywords(profile.dict())

#         # Call LLM to generate resume content
#         resume_html = generate_resume(optimized_profile)

#         return {"resume_html": resume_html}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
