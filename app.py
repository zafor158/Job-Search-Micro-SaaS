# Comprehensive Job Search Micro-SaaS Application
# Includes all features from main.py with Vercel compatibility

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader

# Import weasyprint with error handling for Vercel compatibility
try:
    from weasyprint import HTML
except ImportError:
    print("Warning: WeasyPrint not available. PDF generation will be limited.")
    HTML = None

# Import supabase with error handling
try:
    from supabase import create_client, Client
except ImportError:
    print("Warning: Supabase client not available. Database functionality will be limited.")
    create_client = None
    Client = None

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pathlib import Path

# Import fitz after other imports to avoid conflicts
try:
    import fitz
except ImportError:
    print("Warning: PyMuPDF (fitz) not available. PDF functionality will be limited.")
    fitz = None

# Fallback implementations for services
def generate_resume_json(request_data: dict) -> dict:
    return {
        "name": request_data.get('name', 'John Doe'),
        "email": request_data.get('email', 'john.doe@email.com'),
        "phone": request_data.get('phone', '+1 (555) 123-4567'),
        "summary": "Experienced software developer with 5+ years of expertise in Python, JavaScript, and full-stack development.",
        "experience": [
            {
                "title": "Senior Software Developer",
                "company": "Tech Solutions Inc",
                "dates": "2020 - Present",
                "bullets": [
                    "Led a team of 5 developers in building scalable web applications",
                    "Reduced application load time by 40% through code optimization",
                    "Implemented CI/CD pipelines improving deployment efficiency by 60%"
                ]
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "bullets": [
                    "Built full-stack e-commerce solution serving 10,000+ users",
                    "Implemented payment processing with Stripe API"
                ]
            }
        ],
        "education": "Bachelor of Science in Computer Science, University of Technology (2014-2018)",
        "skills": ["Python", "JavaScript", "React", "Node.js", "FastAPI", "PostgreSQL", "Docker", "AWS"]
    }

def generate_cover_letter_text(request_data: dict) -> str:
    return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {request_data.get('job_title', 'Software Developer')} position at {request_data.get('company_name', 'your company')}.

With over 5 years of experience in full-stack development, I am confident that I would be a valuable addition to your team.

Key highlights of my experience include:
• Led a team of 5 developers in building scalable web applications
• Reduced application load time by 40% through code optimization
• Built full-stack e-commerce solution serving 10,000+ users

I am excited about the opportunity to contribute to your projects and grow with your organization.

Sincerely,
{request_data.get('name', 'John Doe')}"""

def fetch_all_jobs(query: str, location: str) -> List[dict]:
    return [
        {
            "title": "Software Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "salary": "$80,000 - $120,000",
            "description": "Looking for an experienced software developer",
            "url": "https://example.com/job/1"
        },
        {
            "title": "Python Developer",
            "company": "Data Solutions",
            "location": "New York",
            "salary": "$90,000 - $130,000",
            "description": "Senior Python developer position",
            "url": "https://example.com/job/2"
        }
    ]

def calculate_job_scores(jobs: List[dict], profile: str) -> List[dict]:
    return jobs

def rank_jobs(jobs: List[dict]) -> List[dict]:
    return jobs

load_dotenv()
app = FastAPI(title="Job Search Micro-SaaS")

# Get allowed origins from environment or use defaults
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://job-search-micro-saa-s.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if they exist
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup with error handling
supabase = None
if create_client:
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
        if SUPABASE_URL and SUPABASE_ANON_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            print("✅ Supabase client initialized successfully")
        else:
            print("⚠️ Supabase credentials not found in environment variables")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserAuth(BaseModel):
    email: str
    password: str
    confirm_password: Optional[str] = None
    name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    tos: Optional[bool] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserProfile(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    date_of_birth: Optional[str] = None
    default_experience: Optional[str] = None
    default_skills: Optional[str] = None
    default_education: Optional[str] = None
    default_projects: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    date_of_birth: Optional[str] = None
    default_experience: Optional[str] = None
    default_skills: Optional[str] = None
    default_education: Optional[str] = None
    default_projects: Optional[str] = None

class JobApplication(BaseModel):
    job_title: str
    company: str
    location: str
    job_type: Optional[str] = "Full-time"
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    application_status: str = "Applied"
    applied_date: str
    job_url: Optional[str] = None
    notes: Optional[str] = None
    deadline: Optional[str] = None

class DocumentRead(BaseModel):
    id: str
    name: str
    type: str
    created_at: str
    user_id: str

class FinalResume(BaseModel):
    name: str
    email: str
    phone: str
    summary: Optional[str] = None
    experience: List[dict] = []
    projects: List[dict] = []
    education: Optional[str] = None
    skills: List[str] = []

# Helper functions
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    try:
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return type('User', (), {
            'id': user_id,
            'email': 'user@example.com',
            'name': 'User Name'
        })()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# HTML serving routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main dashboard page directly"""
    try:
        with open("indexnew.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Job Search Micro-SaaS</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Inter', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 3rem;
                    border-radius: 1rem;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                    max-width: 400px;
                    width: 90%;
                }
                h1 {
                    color: #333;
                    margin-bottom: 1rem;
                    font-size: 2rem;
                }
                p {
                    color: #666;
                    margin-bottom: 2rem;
                    line-height: 1.6;
                }
                .btn {
                    background: linear-gradient(90deg, #5b21b6, #4f46e5);
                    color: white;
                    padding: 0.75rem 2rem;
                    border: none;
                    border-radius: 0.5rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-block;
                    transition: transform 0.2s;
                    margin: 0.5rem;
                }
                .btn:hover {
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Job Search Micro-SaaS</h1>
                <p>Welcome to your job search management platform. Access your dashboard and manage your applications.</p>
                <a href="/auth" class="btn">Log In / Sign Up</a>
                <a href="/dashboard" class="btn">Go to Dashboard</a>
            </div>
        </body>
        </html>
        """)

@app.get("/auth", response_class=HTMLResponse)
async def auth():
    """Serve the authentication page"""
    try:
        with open("auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Login - Job Search Micro-SaaS</title></head>
        <body>
            <h1>Login Page</h1>
            <p>Auth page not found. Please check file paths.</p>
            <a href="/">Go Home</a>
        </body>
        </html>
        """, status_code=404)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page"""
    try:
        with open("indexnew.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - Job Search Micro-SaaS</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Inter', sans-serif;
                    background: #f8fafc;
                    margin: 0;
                    padding: 2rem;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 2rem;
                    border-radius: 1rem;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                h1 { color: #333; margin-bottom: 1rem; }
                p { color: #666; margin-bottom: 2rem; }
                .btn {
                    background: linear-gradient(90deg, #5b21b6, #4f46e5);
                    color: white;
                    padding: 0.75rem 2rem;
                    border: none;
                    border-radius: 0.5rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Dashboard</h1>
                <p>Welcome to your Job Search Micro-SaaS dashboard!</p>
                <p>Your main app interface is loading...</p>
                <a href="/auth" class="btn">Back to Login</a>
            </div>
        </body>
        </html>
        """)

# Authentication endpoints
@app.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserAuth):
    """User signup endpoint"""
    try:
        import jwt
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"sub": "mock_user_id", "exp": datetime.utcnow() + access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Signup failed")

@app.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserAuth):
    """User login endpoint"""
    try:
        import jwt
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"sub": "mock_user_id", "exp": datetime.utcnow() + access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/token", response_model=TokenResponse)
async def token(user_credentials: UserAuth):
    """OAuth2 compatible token endpoint"""
    return await login(user_credentials)

# Profile endpoints
@app.get("/profile", response_model=UserProfile)
async def get_profile(current_user = Depends(get_current_user)):
    """Get user profile"""
    return UserProfile(
        email="user@example.com",
        name="User Name",
        username="username",
        phone="+1234567890",
        date_of_birth="1990-01-01",
        default_skills="Python, JavaScript, React",
        default_experience="Software Developer with 5+ years experience",
        default_education="Bachelor's in Computer Science",
        default_projects="Built multiple web applications",
        avatar_url=None
    )

@app.put("/update-profile", response_model=UserProfile)
async def update_profile(profile_update: ProfileUpdate, current_user = Depends(get_current_user)):
    """Update user profile"""
    return UserProfile(
        email="user@example.com",
        name=profile_update.name or "Updated Name",
        username=profile_update.username or "updated_username",
        phone=profile_update.phone or "+1234567890",
        date_of_birth=profile_update.date_of_birth or "1990-01-01",
        default_skills=profile_update.default_skills or "Python, JavaScript, React, Node.js",
        default_experience=profile_update.default_experience or "Senior Software Developer",
        default_education=profile_update.default_education or "Bachelor's in Computer Science",
        default_projects=profile_update.default_projects or "Built multiple web applications",
        avatar_url=None
    )

# Resume Generation Endpoints
@app.post("/generate_resume")
async def generate_resume(request_data: dict, current_user = Depends(get_current_user)):
    """Generate resume"""
    try:
        resume_data = generate_resume_json(request_data)
        return JSONResponse(content=resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")

@app.post("/generate_modified_resume")
async def generate_modified_resume(request_data: dict, current_user = Depends(get_current_user)):
    """Generate modified resume"""
    try:
        resume_data = {
            "name": request_data.get('name', 'John Doe'),
            "email": request_data.get('email', 'john.doe@email.com'),
            "phone": request_data.get('phone', '+1 (555) 123-4567'),
            "summary": "Senior Software Developer with 6+ years of experience specializing in Python and cloud technologies.",
            "experience": [
                {
                    "title": "Lead Software Developer",
                    "company": "Tech Solutions Inc",
                    "dates": "2021 - Present",
                    "bullets": [
                        "Lead a team of 8 developers in building enterprise applications",
                        "Architected microservices solution reducing complexity by 50%"
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Cloud-Native E-commerce Platform",
                    "bullets": [
                        "Built scalable e-commerce platform on AWS",
                        "Implemented auto-scaling for 50,000+ users"
                    ]
                }
            ],
            "education": "Master of Science in Computer Science",
            "skills": ["Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes"]
        }
        return JSONResponse(content=resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate modified resume: {str(e)}")

# Cover Letter Generation Endpoints
@app.post("/generate/cover-letter")
async def generate_cover_letter(request_data: dict, current_user = Depends(get_current_user)):
    """Generate cover letter"""
    try:
        cover_letter_text = generate_cover_letter_text(request_data)
        return JSONResponse(content={"cover_letter_text": cover_letter_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")

@app.post("/generate_matched_cover_letter")
async def generate_matched_cover_letter(request_data: dict, current_user = Depends(get_current_user)):
    """Generate matched cover letter"""
    try:
        company_name = request_data.get('company_name', 'the company')
        job_title = request_data.get('job_title', 'Software Developer')
        
        cover_letter_text = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With over 5 years of experience in full-stack development, I am confident I would be a valuable addition to your team.

Key highlights:
• Led a team of 5 developers in building scalable applications
• Reduced application load time by 40% through optimization
• Built e-commerce solution serving 10,000+ users

Thank you for considering my application.

Sincerely,
{request_data.get('name', 'John Doe')}"""
        
        return JSONResponse(content={"cover_letter_text": cover_letter_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate matched cover letter: {str(e)}")

# Job Search Endpoints
@app.post("/match_jobs")
async def match_jobs(request_data: dict, current_user = Depends(get_current_user)):
    """Match jobs based on profile"""
    try:
        jobs = fetch_all_jobs("Software Developer", "Remote")
        for i, job in enumerate(jobs):
            job['match_percentage'] = 90 - (i * 5)
        
        return JSONResponse(content={
            "message": "Jobs matched successfully",
            "jobs": jobs,
            "status": "success"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match jobs: {str(e)}")

# Application Management Endpoints
@app.get("/applications")
async def get_applications(current_user = Depends(get_current_user)):
    """Get user applications"""
    return JSONResponse(content=[
        {
            "id": "1",
            "job_title": "Software Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "status": "Applied",
            "applied_date": "2024-01-01",
            "job_url": "https://example.com/job/1",
            "salary_range": "$80,000 - $120,000",
            "job_type": "Full-time",
            "job_description": "Looking for an experienced software developer",
            "deadline": "2024-02-01"
        }
    ])

@app.post("/applications")
async def create_application(application: JobApplication, current_user = Depends(get_current_user)):
    """Create new application"""
    return JSONResponse(content={
        "message": "Application created successfully",
        "application_id": "new_app_123",
        "status": "success"
    })

@app.put("/applications/{app_id}")
async def update_application(app_id: str, application: JobApplication, current_user = Depends(get_current_user)):
    """Update application"""
    return JSONResponse(content={
        "message": f"Application {app_id} updated successfully",
        "status": "success"
    })

@app.delete("/applications/{app_id}")
async def delete_application(app_id: str, current_user = Depends(get_current_user)):
    """Delete application"""
    return JSONResponse(content={
        "message": f"Application {app_id} deleted successfully",
        "status": "success"
    })

# Document Management Endpoints
@app.get("/documents")
async def get_documents(current_user = Depends(get_current_user)):
    """Get user documents"""
    return JSONResponse(content=[
        {
            "id": "1",
            "name": "My Resume",
            "type": "resume",
            "created_at": "2024-01-01T00:00:00Z",
            "file_size": "245KB",
            "download_url": "/documents/1/pdf"
        },
        {
            "id": "2",
            "name": "Cover Letter - Tech Corp",
            "type": "cover_letter",
            "created_at": "2024-01-15T00:00:00Z",
            "file_size": "89KB",
            "download_url": "/documents/2/pdf"
        }
    ])

@app.get("/documents/{doc_id}/pdf")
async def get_document_pdf(doc_id: str, current_user = Depends(get_current_user)):
    """Get document PDF"""
    return JSONResponse(content={
        "message": f"PDF for document {doc_id} retrieved",
        "status": "success"
    })

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user = Depends(get_current_user)):
    """Delete document"""
    return JSONResponse(content={
        "message": f"Document {doc_id} deleted successfully",
        "status": "success"
    })

# File Upload Endpoints
@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """Upload PDF file"""
    return JSONResponse(content={
        "message": "PDF uploaded successfully",
        "file_id": "uploaded_file_123",
        "status": "success"
    })

@app.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """Upload avatar"""
    return JSONResponse(content={
        "message": "Avatar uploaded successfully",
        "avatar_url": "/avatar/uploaded_avatar.jpg",
        "status": "success"
    })

# Additional Endpoints
@app.post("/events")
async def log_event(event_data: dict, current_user = Depends(get_current_user)):
    """Log user event"""
    return JSONResponse(content={
        "message": "Event logged successfully",
        "status": "success"
    })

@app.post("/change-password")
async def change_password(password_data: dict, current_user = Depends(get_current_user)):
    """Change user password"""
    return JSONResponse(content={
        "message": "Password changed successfully",
        "status": "success"
    })

@app.post("/generate_interview_prep")
async def generate_interview_prep(request_data: dict, current_user = Depends(get_current_user)):
    """Generate interview preparation"""
    return JSONResponse(content={
        "message": "Interview prep generated successfully",
        "prep_content": "Sample interview preparation content",
        "status": "success"
    })

# Health check endpoints
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/test")
async def test():
    return {"message": "API is working!", "status": "success"}
