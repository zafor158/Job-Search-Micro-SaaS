# Clean Job Search Micro-SaaS - Main Application
# Removed user_preferences dependency for cleaner architecture

import os
import json
import uvicorn
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from supabase import create_client, Client
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

# Import services (assuming services.py is in the same directory)
from services import (
    generate_resume_json,
    generate_cover_letter_text,
    fetch_all_jobs,
    calculate_job_scores,
    rank_jobs
)

load_dotenv()
app = FastAPI(title="AI DocGen")

# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
if ALLOWED_ORIGINS == ["*"]:
    ALLOWED_ORIGINS = ["*"]  # Keep wildcard for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

# Use defaults if environment variables are not set
if not SUPABASE_URL:
    SUPABASE_URL = "https://bdcubgmsdprajqagddhr.supabase.co"
    print("Warning: SUPABASE_URL not found in environment variables. Using default.")
    
if not SUPABASE_KEY:
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJkY3ViZ21zZHByYWpxYWdkZGhyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MDk0MzQsImV4cCI6MjA3Mjk4NTQzNH0.5XTt1Q7kBkeMLQ1j7Xo6Yiw3495dTtz8ib7WJx_a8pk"
    print("Warning: SUPABASE_ANON_KEY not found in environment variables. Using default.")

print(f"✅ Using Supabase URL: {SUPABASE_URL}")
print(f"✅ Using Supabase Key: {SUPABASE_KEY[:20]}..." if len(SUPABASE_KEY) > 20 else f"✅ Using Supabase Key: {SUPABASE_KEY}")


# Create Supabase client with error handling
try:
    # Check if we're using environment variables or defaults
    using_env_vars = os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY")
    
    if not using_env_vars:
        print("Warning: Using default Supabase configuration. Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file.")
        print("Creating Supabase client with default values for development...")
    else:
        print("✅ Using Supabase configuration from environment variables.")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully!")
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
    print("The application will run but database features may not work properly.")
    supabase = None

# --- Constants ---
SECRET_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJkY3ViZ21zZHByYWpxYWdkZGhyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzQwOTQzNCwiZXhwIjoyMDcyOTg1NDM0fQ.6myNsqXuo-NsG9wqUaKD58HESSo-cnKChtk0pNWppjo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
_ERROR_THROTTLE_SECONDS = 60

# --- OAuth2 Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Local Storage Setup ---
PROFILE_DIR = Path('data/profiles')
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# --- Pydantic Models ---

class UserAuth(BaseModel):
    email: str
    password: str
    # Optional fields for signup
    name: Optional[str] = None
    username: Optional[str] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    confirm_password: Optional[str] = None
    tos: Optional[bool] = None
    avatar_base64: Optional[str] = None

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
    avatar_url: Optional[str] = None

# UserPreferences model removed - no longer needed

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class AvatarUpdate(BaseModel):
    avatar_base64: str

class ModificationRequest(BaseModel):
    extracted_text: str
    modification_instructions: dict

class Experience(BaseModel):
    title: str
    company: str
    dates: str
    bullets: List[str]

class Project(BaseModel):
    title: str
    bullets: List[str]

class FinalResume(BaseModel):
    name: str
    email: str
    phone: str
    summary: str
    experience: List[Experience]
    projects: List[Project]
    education: str
    skills: List[str]

class CoverLetterRequest(BaseModel):
    user_profile: dict
    job_description: str
    company_name: str
    hiring_manager: Optional[str] = None
    personal_note: Optional[str] = None

class CoverLetterPDFRequest(BaseModel):
    cover_letter_text: str
    user_name: str
    user_email: str
    user_phone: str

class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    score: Optional[float] = None

class InterviewPrepRequest(BaseModel):
    job_description: str
    user_profile: dict
    company_name: str

class InterviewPrepResponse(BaseModel):
    questions: List[str]
    answers: List[str]
    tips: List[str]

class JobMatchRequest(BaseModel):
    query: str
    location: str
    user_profile_text: str

class MatchedCoverLetterRequest(BaseModel):
    job: Job
    user_profile: dict
    personal_note: Optional[str] = None

class JobApplicationCreate(BaseModel):
    company: str
    position: str
    application_status: str = "applied"  # New field: calling_interview, rejected, offering_offered
    job_type: str = "onsite"  # New field: remote, onsite, hybrid
    application_date: Optional[str] = None  # Changed to str to accept ISO date strings
    deadline: Optional[str] = None  # Changed to str to accept ISO date strings
    job_description: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    application_status: Optional[str] = None  # New field
    job_type: Optional[str] = None  # New field
    application_date: Optional[str] = None  # Changed to str to accept ISO date strings
    deadline: Optional[str] = None  # Changed to str to accept ISO date strings
    job_description: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None

class JobApplicationRead(BaseModel):
    id: str
    user_id: str
    company: str
    position: str
    application_status: str
    job_type: str
    application_date: Optional[str] = None
    deadline: Optional[str] = None
    job_description: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_db_record(cls, record: dict):
        """Convert database record to JobApplicationRead object"""
        return cls(
            id=str(record['id']),
            user_id=str(record['user_id']),
            company=record['company'],
            position=record['position'],
            application_status=record.get('application_status', 'applied'),  # Default to 'applied' if missing
            job_type=record.get('job_type', 'onsite'),  # Default to 'onsite' if missing
            application_date=record.get('application_date'),
            deadline=record.get('deadline'),
            job_description=record.get('job_description'),
            salary_range=record.get('salary_range'),
            location=record.get('location'),
            job_url=record.get('job_url'),
            created_at=record['created_at'],
            updated_at=record['updated_at']
        )

class DocumentRead(BaseModel):
    id: str
    doc_type: str
    title: str
    content_json: Optional[dict] = None
    content_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_db_record(cls, record: dict):
        """Create DocumentRead from database record, handling type conversions"""
        # Create a copy of the record and filter out fields not in the model
        filtered_record = {}
        for field in ['id', 'doc_type', 'title', 'content_json', 'content_text', 'created_at', 'updated_at']:
            if field in record:
                filtered_record[field] = record[field]
        
        # Convert id to string if it's an integer
        if isinstance(filtered_record.get('id'), int):
            filtered_record['id'] = str(filtered_record['id'])
        
        # Parse datetime strings if they're strings
        if isinstance(filtered_record.get('created_at'), str):
            from datetime import datetime
            try:
                # Handle different datetime formats
                dt_str = filtered_record['created_at']
                if dt_str.endswith('Z'):
                    dt_str = dt_str[:-1] + '+00:00'
                elif '+' not in dt_str and 'Z' not in dt_str:
                    dt_str += '+00:00'
                filtered_record['created_at'] = datetime.fromisoformat(dt_str)
            except Exception as e:
                print(f"Error parsing created_at: {e}, value: {filtered_record['created_at']}")
                # Use current time as fallback
                filtered_record['created_at'] = datetime.utcnow()
        
        if isinstance(filtered_record.get('updated_at'), str):
            from datetime import datetime
            try:
                # Handle different datetime formats
                dt_str = filtered_record['updated_at']
                if dt_str.endswith('Z'):
                    dt_str = dt_str[:-1] + '+00:00'
                elif '+' not in dt_str and 'Z' not in dt_str:
                    dt_str += '+00:00'
                filtered_record['updated_at'] = datetime.fromisoformat(dt_str)
            except Exception as e:
                print(f"Error parsing updated_at: {e}, value: {filtered_record['updated_at']}")
                # Use current time as fallback
                filtered_record['updated_at'] = datetime.utcnow()
        
        return cls(**filtered_record)

# --- Helper Functions ---

def ensure_profile_exists(user_id: str):
    """Ensure a row exists in public.profiles for the given user_id.
    If not, create a minimal one.
    """
    try:
        result = supabase.table('profiles').select('*').eq('id', user_id).limit(1).execute()
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, tuple) and len(result) >= 1:
            data = result[0]
        else:
            data = result
            
        if not data or len(data) == 0:
            # Get user info from users table
            user_result = supabase.table('users').select('email, name, phone, username, date_of_birth, avatar_url').eq('id', user_id).limit(1).execute()
            # Handle different response formats from Supabase
            if hasattr(user_result, 'data'):
                user_data = user_result.data
            elif isinstance(user_result, tuple) and len(user_result) >= 1:
                user_data = user_result[0]
            else:
                user_data = user_result
            if user_data and len(user_data) > 0:
                user_info = user_data[0]
                basic_payload = {
                    'id': user_id,
                    'email': user_info.get('email', ''),
                    'name': user_info.get('name', ''),
                    'phone': user_info.get('phone', ''),
                    'username': user_info.get('username', ''),
                    'date_of_birth': user_info.get('date_of_birth'),
                    'avatar_url': user_info.get('avatar_url', ''),
                    'default_experience': '',
                    'default_skills': '',
                    'default_education': '',
                    'default_projects': ''
                }
                ins, _ = supabase.table('profiles').insert(basic_payload).execute()
                print(f"Created profile for user: {user_id}")
            else:
                # Fallback minimal profile
                data, _ = supabase.table('profiles').select('*').eq('id', user_id).limit(1).execute()
                if not data or len(data) == 0:
                    minimal_payload = {
                        'id': user_id,
                        'email': '',
                        'name': '',
                        'phone': '',
                        'username': '',
                        'default_experience': '',
                        'default_skills': '',
                        'default_education': '',
                        'default_projects': ''
                    }
                    ins, _ = supabase.table('profiles').insert(minimal_payload).execute()
                    print(f"Created minimal profile for user: {user_id}")
    except Exception as e:
        print(f"Error ensuring profile exists: {e}")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    try:
        print(f"Authenticating user with token: {token[:20]}...")
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        print(f"Decoded user_id: {user_id}")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify user exists in database
        try:
            if supabase is None:
                print("Supabase client is None in get_current_user")
                raise HTTPException(status_code=503, detail="Database not available")
                
            print(f"Querying users table for user_id: {user_id}")
            result = supabase.table('users').select('*').eq('id', user_id).limit(1).execute()
            print(f"User query result: {result}")
            
            # Handle different response formats from Supabase
            if hasattr(result, 'data'):
                data = result.data
            elif isinstance(result, tuple) and len(result) >= 1:
                data = result[0]
            else:
                data = result
            
            if not data or len(data) == 0:
                print(f"No user found for user_id: {user_id}")
                raise HTTPException(status_code=401, detail="User not found")
            
            user_data = data[0]
            print(f"User authenticated successfully: {user_data.get('email', 'no email')}")
            return type('User', (), {
                'id': user_data['id'],
                'email': user_data['email'],
                'name': user_data.get('name'),
                'username': user_data.get('username')
            })()
        except Exception as db_err:
            print(f"Database error in get_current_user: {db_err}")
            print(f"Database error type: {type(db_err)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="User verification failed")
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def save_document_to_db(user_id: str, doc_type: str, title: str, content_json: dict = None, content_text: str = None):
    """Save document to database"""
    try:
        payload = {
            'user_id': user_id,
            'doc_type': doc_type,
            'title': title,
            'content_json': content_json,
            'content_text': content_text,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        supabase.table("documents").insert([payload]).execute()
        print(f"Document saved to DB: {title}")
    except Exception as e:
        print(f"Failed to save document to DB: {e}")

# --- Local JSON fallback for profiles ---

def local_profile_path(user_id: str) -> Path:
    return PROFILE_DIR / f"{user_id}.json"

def read_local_profile(user_id: str) -> dict:
    try:
        p = local_profile_path(user_id)
        if not p.exists():
            return {}
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to read local profile: {e}")
        return {}

def write_local_profile(user_id: str, profile: dict):
    try:
        p = local_profile_path(user_id)
        with p.open('w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to write local profile: {e}")

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Job Search Micro-SaaS API"}

@app.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserAuth):
    """Custom signup endpoint that stores user data directly in profiles table"""
    email = user_data.email
    password = user_data.password
    
    # Validate signup data
    if user_data.confirm_password and password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if user_data.tos is not None and not user_data.tos:
        raise HTTPException(status_code=400, detail="You must agree to the Terms of Service")
    
    # Check if user already exists
    try:
        existing_user_result = supabase.table('users').select('id').eq('email', email).limit(1).execute()
        if existing_user_result.data and len(existing_user_result.data) > 0:
            raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        print(f"Error checking existing user: {e}")
        raise HTTPException(status_code=500, detail="Database error during signup")
    
    # Generate user ID
    import uuid
    user_id = str(uuid.uuid4())
    
    # Hash password
    import bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user in users table
    user_data_dict = {
        'id': user_id,
        'email': email,
        'password_hash': password_hash,
        'name': user_data.name or '',
        'phone': user_data.phone or '',
        'username': user_data.username or '',
        'date_of_birth': user_data.dob,
        'avatar_url': user_data.avatar_base64 or '',
        'is_active': True,
        'email_verified': False
    }
    
    try:
        # Insert user into users table
        supabase.table('users').insert(user_data_dict).execute()
        print(f"User created in users table: {user_id}")
    except Exception as user_err:
        print(f"Failed to create user in users table: {user_err}")
        raise HTTPException(status_code=500, detail="Failed to create user account")
    
    # Create profile in profiles table (only existing columns)
    profile_data = {
        'id': user_id,
        'email': email,
        'name': user_data.name or '',
        'phone': user_data.phone or '',
        'username': user_data.username or '',
        'date_of_birth': user_data.dob,
        'avatar_url': user_data.avatar_base64 or ''
    }
    
    try:
        supabase.table('profiles').insert(profile_data).execute()
        print(f"Profile created in profiles table: {user_id}")
    except Exception as profile_err:
        print(f"Failed to create profile in profiles table: {profile_err}")
        # Try to create minimal profile (only existing columns)
        try:
            minimal_profile = {
                'id': user_id,
                'email': email,
                'name': '',
                'phone': '',
                'username': '',
                'date_of_birth': None,
                'avatar_url': ''
            }
            supabase.table('profiles').insert(minimal_profile).execute()
            print(f"Minimal profile created: {user_id}")
        except Exception as minimal_err:
            print(f"Failed to create minimal profile: {minimal_err}")
    
    # User preferences creation removed - no longer needed
    print(f"User created successfully: {user_id}")
    
    # Save profile locally as backup
    try:
        local_profile = { 
            'email': email, 
            'name': '', 
            'phone': '',
            'username': '',
            'date_of_birth': None,
            'default_experience': '',
            'default_skills': '',
            'default_education': '',
            'default_projects': '',
            'avatar_url': ''
        }
        write_local_profile(user_id, local_profile)
        print(f"Local profile backup created: {user_id}")
    except Exception as local_err:
        print(f"Failed to create local profile backup: {local_err}")
    
    # Generate JWT token
    import jwt
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": user_id, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserAuth):
    """Login endpoint"""
    email = user_credentials.email
    password = user_credentials.password
    
    try:
        # Get user from database
        result = supabase.table('users').select('*').eq('email', email).limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = result.data[0]
        stored_password_hash = user.get('password_hash')
        
        if not stored_password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        import bcrypt
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is active
        if not user.get('is_active', True):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Generate JWT token
        import jwt
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"sub": user['id'], "exp": datetime.utcnow() + access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/token", response_model=TokenResponse)
async def token(user_credentials: UserAuth):
    """OAuth2 compatible token endpoint (alias for login)"""
    return await login(user_credentials)

# --- Preferences Endpoints Removed ---
# User preferences functionality has been removed from the application

# --- Job Applications Endpoints ---

@app.post("/job-applications", response_model=dict)
async def create_job_application(application: JobApplicationCreate, current_user = Depends(get_current_user)):
    """Create a new job application"""
    user_id = current_user.id
    
    try:
        print(f"Creating job application for user_id: {user_id}")
        print(f"Application data: {application.dict()}")
        
        # Create app_data with all fields for the new schema (removed status)
        app_data = {
            'user_id': user_id,
            'company': application.company,
            'position': application.position,
            'application_status': application.application_status,
            'job_type': application.job_type,
            'application_date': application.application_date,
            'deadline': application.deadline,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add optional fields only if they have values
        if application.job_description:
            app_data['job_description'] = application.job_description
        if application.salary_range:
            app_data['salary_range'] = application.salary_range
        if application.location:
            app_data['location'] = application.location
        if application.job_url:
            app_data['job_url'] = application.job_url
        
        print(f"Prepared app_data: {app_data}")
        
        result = supabase.table("job_applications").insert([app_data]).execute()
        print(f"Supabase insert result: {result}")
        print(f"Result type: {type(result)}")
        
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, tuple) and len(result) >= 1:
            data = result[0]
        else:
            data = result
        
        print(f"Processed data: {data}")
        print(f"Data type: {type(data)}")
        
        if data and len(data) > 0:
            print(f"Successfully created application with ID: {data[0]['id']}")
            # Get user profile for email notification
            try:
                prof_result = supabase.table('profiles').select('email, name').eq('id', current_user.id).limit(1).execute()
                # Handle different response formats from Supabase
                if hasattr(prof_result, 'data'):
                    prof = prof_result.data
                elif isinstance(prof_result, tuple) and len(prof_result) >= 1:
                    prof = prof_result[0]
                else:
                    prof = prof_result
                    
                if prof and len(prof) > 0:
                    user_email = prof[0].get('email')
                    user_name = prof[0].get('name', 'User')
                    print(f"Job application created for {user_name} ({user_email})")
            except Exception as profile_err:
                print(f"Failed to get user profile for notification: {profile_err}")
            
            return {"message": "Job application created successfully", "id": data[0]['id']}
        else:
            print("Failed to create application - no data returned")
            raise HTTPException(status_code=500, detail="Failed to create job application")
            
    except Exception as e:
        print(f"Error creating job application: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job application")

@app.get("/job-applications")
async def get_job_applications(current_user = Depends(get_current_user)):
    """Get all job applications for the current user"""
    user_id = current_user.id
    
    try:
        result = supabase.table("job_applications").select("*").eq('user_id', user_id).order("application_date", desc=True).execute()
        
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, tuple) and len(result) >= 1:
            data = result[0]
        else:
            data = result
        
        print(f"Job applications query result: {result}")
        print(f"Data type: {type(data)}, Data: {data}")
        
        # Ensure data is a list
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except json.JSONDecodeError:
                print(f"Failed to parse data as JSON: {data}")
                return []
        
        if data and isinstance(data, list):
            print(f"Found {len(data)} job applications")
            applications = []
            for app in data:
                try:
                    # Convert to dictionary format for frontend
                    converted_app = {
                        'id': str(app['id']),
                        'user_id': str(app['user_id']),
                        'company': app['company'],
                        'position': app['position'],
                        'application_status': app.get('application_status', 'applied'),
                        'job_type': app.get('job_type', 'onsite'),
                        'application_date': app.get('application_date'),
                        'deadline': app.get('deadline'),
                        'job_description': app.get('job_description'),
                        'salary_range': app.get('salary_range'),
                        'location': app.get('location'),
                        'job_url': app.get('job_url'),
                        'created_at': app['created_at'],
                        'updated_at': app['updated_at']
                    }
                    applications.append(converted_app)
                except Exception as app_err:
                    print(f"Error converting application {app.get('id', 'unknown')}: {app_err}")
                    continue
            
            print(f"Successfully converted {len(applications)} applications")
            return applications
        else:
            print("No job applications found for user")
            return []
            
    except Exception as e:
        print(f"Error fetching job applications: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch job applications")

@app.put("/job-applications/{application_id}", response_model=dict)
async def update_job_application(application_id: str, application: JobApplicationUpdate, current_user = Depends(get_current_user)):
    """Update a job application"""
    user_id = current_user.id
    
    try:
        # Check if application exists and belongs to user
        existing_result = supabase.table("job_applications").select("*").eq("id", application_id).eq('user_id', user_id).execute()
        
        # Handle different response formats from Supabase
        if hasattr(existing_result, 'data'):
            existing_data = existing_result.data
        elif isinstance(existing_result, tuple) and len(existing_result) >= 1:
            existing_data = existing_result[0]
        else:
            existing_data = existing_result
            
        if not existing_data or len(existing_data) == 0:
            raise HTTPException(status_code=404, detail="Job application not found")
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if application.company is not None:
            update_data['company'] = application.company
        if application.position is not None:
            update_data['position'] = application.position
        if application.application_status is not None:
            update_data['application_status'] = application.application_status
        if application.job_type is not None:
            update_data['job_type'] = application.job_type
        if application.application_date is not None:
            update_data['application_date'] = application.application_date  # Already a string
        if application.deadline is not None:
            update_data['deadline'] = application.deadline  # Already a string
        if application.job_description is not None:
            update_data['job_description'] = application.job_description
        if application.salary_range is not None:
            update_data['salary_range'] = application.salary_range
        if application.location is not None:
            update_data['location'] = application.location
        if application.job_url is not None:
            update_data['job_url'] = application.job_url
        
        result = supabase.table("job_applications").update(update_data).eq("id", application_id).eq('user_id', user_id).execute()
        
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, tuple) and len(result) >= 1:
            data = result[0]
        else:
            data = result
        
        if data and len(data) > 0:
            # Get user profile for email notification
            try:
                profile_result = supabase.table('profiles').select('email, name').eq('id', user_id).limit(1).execute()
                # Handle different response formats from Supabase
                if hasattr(profile_result, 'data'):
                    profile_resp = profile_result.data
                elif isinstance(profile_result, tuple) and len(profile_result) >= 1:
                    profile_resp = profile_result[0]
                else:
                    profile_resp = profile_result
                    
                if profile_resp and len(profile_resp) > 0:
                    user_email = profile_resp[0].get('email')
                    user_name = profile_resp[0].get('name', 'User')
                    print(f"Job application updated for {user_name} ({user_email})")
            except Exception as profile_err:
                print(f"Failed to get user profile for notification: {profile_err}")
            
            return {"message": "Job application updated successfully", "id": application_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to update job application")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating job application: {e}")
        raise HTTPException(status_code=500, detail="Failed to update job application")

@app.delete("/job-applications/{application_id}")
async def delete_job_application(application_id: str, current_user = Depends(get_current_user)):
    """Delete a job application"""
    user_id = current_user.id
    
    try:
        result = supabase.table("job_applications").delete().eq("id", application_id).eq('user_id', user_id).execute()
        
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, tuple) and len(result) >= 1:
            data = result[0]
        else:
            data = result
        
        if data and len(data) > 0:
            return {"message": "Job application deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Job application not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting job application: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete job application")

# --- Test Endpoint for Database Connection ---

@app.get("/test-db")
async def test_database():
    """Test database connection and table existence"""
    try:
        if not supabase:
            return {"status": "error", "message": "Supabase client not initialized"}
        
        # Test basic connection
        result = supabase.table('users').select('count').execute()
        
        # Test documents table
        docs_result = supabase.table('documents').select('count').execute()
        
        # Test job_applications table
        apps_result = supabase.table('job_applications').select('count').execute()
        
        return {
            "status": "success",
            "message": "Database connection working",
            "users_table": "exists",
            "documents_table": "exists",
            "job_applications_table": "exists",
            "supabase_url": SUPABASE_URL
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database test failed: {str(e)}",
            "supabase_url": SUPABASE_URL
        }

@app.post("/test-create-application")
async def test_create_application(current_user = Depends(get_current_user)):
    """Test endpoint to manually create a job application"""
    user_id = current_user.id
    
    try:
        test_app_data = {
            'user_id': user_id,
            'company': 'Test Company',
            'position': 'Test Position',
            'status': 'applied',
            'application_date': datetime.utcnow().isoformat(),
            'notes': 'Test application',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        print(f"Testing application creation for user_id: {user_id}")
        print(f"Test data: {test_app_data}")
        
        result = supabase.table("job_applications").insert([test_app_data]).execute()
        print(f"Test insert result: {result}")
        
        return {"message": "Test application created", "result": str(result)}
        
    except Exception as e:
        print(f"Test creation error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# --- Documents Endpoints ---

@app.get("/documents", response_model=List[DocumentRead])
async def get_documents(current_user = Depends(get_current_user)):
    """Get all documents for the current user"""
    user_id = current_user.id
    
    try:
        print(f"Fetching documents for user_id: {user_id}")
        
        # Check if supabase client is available
        if not supabase:
            print("Error: Supabase client not initialized")
            # Return empty list instead of error for better UX
            return []
        
        # Try to fetch documents
        result = supabase.table("documents").select("*").eq('user_id', user_id).order("created_at", desc=True).limit(20).execute()
        
        print(f"Supabase query result: {result}")
        print(f"Result type: {type(result)}")
        
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
            count = result.count
        elif isinstance(result, tuple) and len(result) == 2:
            data, count = result
        else:
            print(f"Unexpected result format: {result}")
            return []
        
        print(f"Data: {data}, Count: {count}")
        print(f"Data type: {type(data)}, Count type: {type(count)}")
        
        # Ensure data is a list
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except json.JSONDecodeError:
                print(f"Failed to parse data as JSON: {data}")
                return []
        
        if data and isinstance(data, list) and len(data) > 0:
            print(f"Found {len(data)} documents")
            # Convert to DocumentRead objects
            documents = []
            for i, doc in enumerate(data):
                if isinstance(doc, dict):
                    print(f"Processing document {i+1}: {doc.get('title', 'no title')}")
                    try:
                        converted_doc = DocumentRead.from_db_record(doc)
                        documents.append(converted_doc)
                        print(f"Successfully converted document {i+1}")
                    except Exception as doc_err:
                        print(f"Error converting document {doc.get('id', 'unknown')}: {doc_err}")
                        print(f"Document data: {doc}")
                        import traceback
                        traceback.print_exc()
                        # Skip invalid documents
                        continue
                else:
                    print(f"Document {i+1} is not a dict: {type(doc)} - {doc}")
                    continue
            
            print(f"Successfully converted {len(documents)} documents")
            return documents
        else:
            print("No documents found for user")
            return []
            
    except Exception as e:
        print(f"Error fetching documents: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of error for better UX
        return []

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str, current_user = Depends(get_current_user)):
    """Delete a document"""
    user_id = current_user.id
    
    try:
        data, count = supabase.table("documents").delete().eq("id", document_id).eq('user_id', user_id).execute()
        
        if data and len(data) > 0:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(document_id: str, current_user = Depends(get_current_user)):
    """Get a specific document"""
    user_id = current_user.id
    
    try:
        data, count = supabase.table('documents').select('*').eq('id', document_id).eq('user_id', user_id).limit(1).execute()
        
        if data and len(data) > 0:
            return DocumentRead(**data[0])
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching document: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")

@app.get("/documents/{document_id}/pdf")
async def get_document_pdf(document_id: str, current_user = Depends(get_current_user)):
    """Get a document as PDF"""
    user_id = current_user.id
    
    try:
        # Get document from database
        result = supabase.table('documents').select('*').eq('id', document_id).eq('user_id', user_id).limit(1).execute()
        
        # Handle different response formats from Supabase
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, tuple) and len(result) >= 1:
            data = result[0]
        else:
            data = result
        
        if not data or len(data) == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = data[0]
        doc_type = document.get('doc_type')
        content_json = document.get('content_json')
        content_text = document.get('content_text')
        
        # Generate PDF based on document type
        if doc_type == 'resume' and content_json:
            # Generate resume PDF
            final_resume = FinalResume(
                name=content_json.get('name', 'Your Name'),
                email=content_json.get('email', ''),
                phone=content_json.get('phone', ''),
                summary=content_json.get('summary', ''),
                experience=content_json.get('experience', []),
                projects=content_json.get('projects', []),
                education=content_json.get('education', 'N/A'),
                skills=content_json.get('skills', [])
            )
            
            # Load template
            env = Environment(loader=FileSystemLoader('Template'))
            template = env.get_template('resume_template.html')
            
            # Render template with data
            html_content = template.render(**final_resume.dict())
            
            # Generate PDF
            pdf_buffer = HTML(string=html_content).write_pdf()
            
            return Response(
                content=pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"inline; filename=resume_{document_id}.pdf"}
            )
            
        elif doc_type == 'cover_letter' and content_text:
            # Generate cover letter PDF
            # Extract name, email, phone from content_text if available
            name = 'Your Name'
            email = 'your.email@example.com'
            phone = ''
            
            # Try to extract from content_text
            lines = content_text.split('\n')
            for i, line in enumerate(lines):
                if 'Sincerely' in line or 'Best regards' in line:
                    if i + 1 < len(lines):
                        potential_name = lines[i + 1].strip()
                        if potential_name and not name:
                            name = potential_name
                    for j in range(i + 2, min(i + 5, len(lines))):
                        line_content = lines[j].strip()
                        if '@' in line_content and not email:
                            email = line_content
                        elif any(char.isdigit() for char in line_content) and not phone:
                            phone = line_content
                    break
            
            # Load template
            env = Environment(loader=FileSystemLoader('Template'))
            template = env.get_template('cover_letter_template.html')
            
            # Render template with data
            html_content = template.render(
                cover_letter_text=content_text,
                name=name,
                email=email,
                phone=phone
            )
            
            # Generate PDF
            pdf_buffer = HTML(string=html_content).write_pdf()
            
            return Response(
                content=pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"inline; filename=cover_letter_{document_id}.pdf"}
            )
        else:
            raise HTTPException(status_code=400, detail="Document content not available for PDF generation")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating document PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate document PDF")

# --- Resume Generation Endpoints ---

@app.post("/generate-resume")
async def generate_resume(request_data: dict, current_user = Depends(get_current_user)):
    """Generate resume from user profile or PDF"""
    user_id = current_user.id
    
    try:
        # Validate request data
        if not request_data:
            raise HTTPException(status_code=400, detail="Request data is required")
        
        # Generate resume using the service
        resume_data = generate_resume_json(request_data)
        
        # Save to database
        title = f"Resume - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        save_document_to_db(user_id, "resume", title, resume_data)
        
        return resume_data
        
    except ValueError as e:
        print(f"Validation error generating resume: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error generating resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")

@app.post("/generate-cover-letter")
async def generate_cover_letter(request: CoverLetterRequest, current_user = Depends(get_current_user)):
    """Generate cover letter"""
    user_id = current_user.id
    
    try:
        # Debug logging
        print(f"Cover letter request received:")
        print(f"  user_profile: {type(request.user_profile)} - {bool(request.user_profile)}")
        print(f"  job_description: {type(request.job_description)} - {len(request.job_description) if request.job_description else 0} chars")
        print(f"  company_name: {type(request.company_name)} - {request.company_name}")
        print(f"  hiring_manager: {request.hiring_manager}")
        print(f"  personal_note: {request.personal_note}")
        
        # Validate request data
        if not request.user_profile:
            raise HTTPException(status_code=400, detail="User profile is required")
        
        if not request.job_description or not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
            
        if not request.company_name or not request.company_name.strip():
            raise HTTPException(status_code=400, detail="Company name is required")
        
        # Generate cover letter using the service
        cover_letter_text = generate_cover_letter_text(request.dict())
        
        # Save to database
        title = f"Cover Letter - {request.company_name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        save_document_to_db(user_id, "cover_letter", title, None, cover_letter_text)
        
        return {"cover_letter_text": cover_letter_text}
        
    except ValueError as e:
        print(f"Validation error generating cover letter: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")

# --- Job Search Endpoints ---

@app.post("/search-jobs")
async def search_jobs(request: JobMatchRequest):
    """Search for jobs and match with user profile"""
    try:
        # Fetch jobs from all sources
        jobs = fetch_all_jobs(request.query, request.location)
        
        if not jobs:
            return {"jobs": [], "message": "No jobs found"}
        
        # Calculate job scores
        scored_jobs = calculate_job_scores(request.user_profile_text, jobs)
        
        # Rank and return top jobs
        ranked_jobs = rank_jobs(scored_jobs, top_n=20)
        
        return {"jobs": ranked_jobs}
        
    except Exception as e:
        print(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to search jobs")

@app.post("/generate-matched-cover-letter")
async def generate_matched_cover_letter(request: MatchedCoverLetterRequest, current_user = Depends(get_current_user)):
    """Generate cover letter for a specific job"""
    user_id = current_user.id
    
    try:
        # Debug logging
        print(f"Matched cover letter request received:")
        print(f"  user_profile: {type(request.user_profile)} - {bool(request.user_profile)}")
        print(f"  job: {type(request.job)} - {request.job.title if request.job else 'None'}")
        print(f"  personal_note: {request.personal_note}")
        
        # Validate request data
        if not request.user_profile:
            raise HTTPException(status_code=400, detail="User profile is required")
        
        if not request.job:
            raise HTTPException(status_code=400, detail="Job details are required")
        
        # Create cover letter request
        cover_letter_request = CoverLetterRequest(
            user_profile=request.user_profile,
            job_description=request.job.description,
            company_name=request.job.company,
            personal_note=request.personal_note
        )
        
        # Generate cover letter
        cover_letter_text = generate_cover_letter_text(cover_letter_request.dict())
        
        # Save to database
        title = f"Cover Letter - {request.job.company} - {request.job.title} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        save_document_to_db(user_id, "cover_letter", title, None, cover_letter_text)
        
        return {"cover_letter_text": cover_letter_text}
        
    except Exception as e:
        print(f"Error generating matched cover letter: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cover letter")

# --- Profile Endpoints ---

@app.get("/profile", response_model=UserProfile)
async def get_profile(current_user = Depends(get_current_user)):
    """Get user profile"""
    user_id = current_user.id
    
    try:
        # Try to get profile from database
        result = supabase.table('profiles').select('*').eq('id', user_id).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            profile_data = result.data[0]
            return UserProfile(
                email=profile_data.get('email', ''),
                name=profile_data.get('name'),
                phone=profile_data.get('phone'),
                username=profile_data.get('username'),
                date_of_birth=profile_data.get('date_of_birth'),
                default_experience=profile_data.get('default_experience'),
                default_skills=profile_data.get('default_skills'),
                default_education=profile_data.get('default_education'),
                default_projects=profile_data.get('default_projects'),
                avatar_url=profile_data.get('avatar_url')
            )
        else:
            # Fallback to local profile
            profile = read_local_profile(user_id) or {}
            return UserProfile(
                email=profile.get('email', ''),
                name=profile.get('name'),
                phone=profile.get('phone'),
                username=profile.get('username'),
                date_of_birth=profile.get('date_of_birth'),
                default_experience=profile.get('default_experience'),
                default_skills=profile.get('default_skills'),
                default_education=profile.get('default_education'),
                default_projects=profile.get('default_projects'),
                avatar_url=profile.get('avatar_url')
            )
            
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")

@app.put("/profile", response_model=UserProfile)
async def update_profile(profile_update: ProfileUpdate, current_user = Depends(get_current_user)):
    """Update user profile"""
    user_id = current_user.id
    
    try:
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if profile_update.name is not None:
            update_data['name'] = profile_update.name
        if profile_update.phone is not None:
            update_data['phone'] = profile_update.phone
        if profile_update.username is not None:
            update_data['username'] = profile_update.username
        if profile_update.date_of_birth is not None:
            update_data['date_of_birth'] = profile_update.date_of_birth
        if profile_update.default_experience is not None:
            update_data['default_experience'] = profile_update.default_experience
        if profile_update.default_skills is not None:
            update_data['default_skills'] = profile_update.default_skills
        if profile_update.default_education is not None:
            update_data['default_education'] = profile_update.default_education
        if profile_update.default_projects is not None:
            update_data['default_projects'] = profile_update.default_projects
        if profile_update.avatar_url is not None:
            update_data['avatar_url'] = profile_update.avatar_url
        
        # Update in database
        data, count = supabase.table('profiles').update(update_data).eq('id', user_id).execute()
        
        if data and len(data) > 0:
            updated_profile = data[0]
            return UserProfile(
                email=updated_profile.get('email', ''),
                name=updated_profile.get('name'),
                phone=updated_profile.get('phone'),
                username=updated_profile.get('username'),
                date_of_birth=updated_profile.get('date_of_birth'),
                default_experience=updated_profile.get('default_experience'),
                default_skills=updated_profile.get('default_skills'),
                default_education=updated_profile.get('default_education'),
                default_projects=updated_profile.get('default_projects'),
                avatar_url=updated_profile.get('avatar_url')
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update profile")
            
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

# --- Dashboard Endpoint ---

@app.get("/dashboard")
async def get_dashboard(current_user = Depends(get_current_user)):
    """Get dashboard data for the current user"""
    user_id = current_user.id
    
    try:
        # Get user profile
        profile = {}
        try:
            data, count = supabase.table('profiles').select('*').eq('id', user_id).limit(1).execute()
            if data and len(data) > 0:
                profile = data[0]
        except Exception as db_err:
            print(f"Failed to read profile from DB: {db_err}")
            profile = read_local_profile(user_id) or {}
        
        # User preferences removed - no longer needed
        preferences = {}
        
        # Get recent applications count
        applications_count = 0
        try:
            apps_data, count = supabase.table('job_applications').select('id').eq('user_id', user_id).execute()
            if apps_data:
                applications_count = len(apps_data)
        except Exception as apps_err:
            print(f"Failed to read applications from DB: {apps_err}")
        
        # Get recent documents count
        documents_count = 0
        try:
            docs_data, count = supabase.table('documents').select('id').eq('user_id', user_id).execute()
            if docs_data:
                documents_count = len(docs_data)
        except Exception as docs_err:
            print(f"Failed to read documents from DB: {docs_err}")
        
        return {
            "profile": profile,
            "preferences": preferences,
            "applications_count": applications_count,
            "documents_count": documents_count
        }
        
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

# --- Interview Prep Endpoint ---

@app.post("/generate_interview_prep")
async def generate_interview_prep(request: InterviewPrepRequest, current_user = Depends(get_current_user)):
    """Generate interview preparation questions and answers"""
    try:
        # Generate interview prep content using AI
        system_prompt = f"""
        You are an expert career coach preparing someone for an interview at {request.company} for the position of {request.job_title}.
        
        Generate:
        1. 5-7 relevant interview questions they might be asked
        2. Sample answers for each question
        3. 3-5 tips for success in this interview
        
        Format your response as JSON with keys: "questions", "answers", "tips"
        """
        
        user_content = f"""
        Job Title: {request.job_title}
        Company: {request.company}
        Job Description: {request.job_description}
        """
        
        # Use Groq API to generate content
        from groq import Groq
        import os
        
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        
        content = chat_completion.choices[0].message.content
        interview_data = json.loads(content)
        
        return interview_data
        
    except Exception as e:
        print(f"Error generating interview prep: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate interview prep")

# --- Password Change Endpoint ---

@app.put("/change-password")
async def change_password(password_change: PasswordChange, current_user = Depends(get_current_user)):
    """Change user password"""
    user_id = current_user.id
    
    try:
        # Get current user data
        user_data, _ = supabase.table('users').select('password_hash').eq('id', user_id).limit(1).execute()
        
        if not user_data or len(user_data) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        stored_password_hash = user_data[0].get('password_hash')
        
        # Verify current password
        import bcrypt
        if not bcrypt.checkpw(password_change.current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(password_change.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password in database
        supabase.table('users').update({
            'password_hash': new_password_hash,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

# --- Avatar Update Endpoint ---

@app.put("/avatar")
async def update_avatar(avatar_update: AvatarUpdate, current_user = Depends(get_current_user)):
    """Update user avatar"""
    user_id = current_user.id
    
    try:
        # Update avatar in users table
        supabase.table('users').update({
            'avatar_url': avatar_update.avatar_base64,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()
        
        # Update avatar in profiles table
        data, count = supabase.table('profiles').update({
            'avatar_url': avatar_update.avatar_base64,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()
        
        if data and len(data) > 0:
            return {"message": "Avatar updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update avatar")
            
    except Exception as e:
        print(f"Error updating avatar: {e}")
        raise HTTPException(status_code=500, detail="Failed to update avatar")

# --- Missing Endpoints for Frontend Compatibility ---

@app.post("/generate_resume")
async def generate_resume_alt(request_data: dict, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await generate_resume(request_data, current_user)


@app.post("/generate_modified_resume")
async def generate_modified_resume(request_data: dict, current_user = Depends(get_current_user)):
    """Generate modified resume from PDF with instructions"""
    user_id = current_user.id
    
    try:
        # This is essentially the same as generate_resume but with extracted_text
        resume_data = generate_resume_json(request_data)
        
        # Save to database
        title = f"Modified Resume - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        save_document_to_db(user_id, "resume", title, resume_data)
        
        return resume_data
        
    except Exception as e:
        print(f"Error generating modified resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate modified resume")

@app.post("/generate/cover-letter")
async def generate_cover_letter_alt(request: CoverLetterRequest, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await generate_cover_letter(request, current_user)

@app.post("/match_jobs")
async def match_jobs_alt(request: JobMatchRequest):
    """Alternative endpoint for frontend compatibility"""
    return await search_jobs(request)

@app.post("/generate_matched_cover_letter")
async def generate_matched_cover_letter_alt(request: MatchedCoverLetterRequest, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await generate_matched_cover_letter(request, current_user)

@app.get("/applications", response_model=List[dict])
async def get_applications_alt(current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await get_job_applications(current_user)

@app.post("/applications", response_model=dict)
async def create_application_alt(application: JobApplicationCreate, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await create_job_application(application, current_user)

@app.put("/applications/{application_id}", response_model=dict)
async def update_application_alt(application_id: str, application: JobApplicationUpdate, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await update_job_application(application_id, application, current_user)

@app.delete("/applications/{application_id}")
async def delete_application_alt(application_id: str, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await delete_job_application(application_id, current_user)

@app.put("/update_profile", response_model=UserProfile)
async def update_profile_alt(profile_update: ProfileUpdate, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await update_profile(profile_update, current_user)

@app.put("/change_password")
async def change_password_alt(password_change: PasswordChange, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await change_password(password_change, current_user)

@app.put("/update_avatar")
async def update_avatar_alt(avatar_update: AvatarUpdate, current_user = Depends(get_current_user)):
    """Alternative endpoint for frontend compatibility"""
    return await update_avatar(avatar_update, current_user)


@app.post("/events")
async def log_event(event_data: dict, current_user = Depends(get_current_user)):
    """Log user events for analytics"""
    try:
        # This is a placeholder implementation
        # You can implement actual event logging here
        print(f"Event logged: {event_data}")
        return {"message": "Event logged successfully"}
        
    except Exception as e:
        print(f"Error logging event: {e}")
        raise HTTPException(status_code=500, detail="Failed to log event")

# --- PDF Generation Endpoints ---

@app.post("/export/pdf")
async def export_resume_pdf(resume_data: dict, current_user = Depends(get_current_user)):
    """Export resume as PDF - frontend compatibility endpoint"""
    user_id = current_user.id
    
    try:
        # Convert dict to FinalResume model
        final_resume = FinalResume(
            name=resume_data.get('name', 'Your Name'),
            email=resume_data.get('email', ''),
            phone=resume_data.get('phone', ''),
            summary=resume_data.get('summary', ''),
            experience=resume_data.get('experience', []),
            projects=resume_data.get('projects', []),
            education=resume_data.get('education', 'N/A'),
            skills=resume_data.get('skills', [])
        )
        
        # Load template
        env = Environment(loader=FileSystemLoader('Template'))
        template = env.get_template('resume_template.html')
        
        # Render template with data
        html_content = template.render(**final_resume.dict())
        
        # Generate PDF
        pdf_buffer = HTML(string=html_content).write_pdf()
        
        # Return PDF as response
        return Response(
            content=pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resume_{user_id}.pdf"}
        )
        
    except Exception as e:
        print(f"Error exporting resume PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to export resume PDF")

@app.post("/export/cover-letter/pdf")
async def export_cover_letter_pdf(request_data: dict, current_user = Depends(get_current_user)):
    """Export cover letter as PDF - frontend compatibility endpoint"""
    user_id = current_user.id
    
    try:
        # Extract data from request
        cover_letter_text = request_data.get('cover_letter_text', '')
        name = request_data.get('name', '')
        email = request_data.get('email', '')
        phone = request_data.get('phone', '')
        
        # Check if cover letter text is empty
        if not cover_letter_text or len(cover_letter_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Cover letter text is empty. Please generate a cover letter first.")
        
        # If profile info is missing, try to extract from cover letter text
        if not name or not email:
            # Look for signature pattern in cover letter text
            lines = cover_letter_text.split('\n')
            for i, line in enumerate(lines):
                if 'Sincerely' in line or 'Best regards' in line:
                    # Next line should be the name
                    if i + 1 < len(lines):
                        potential_name = lines[i + 1].strip()
                        if potential_name and not name:
                            name = potential_name
                    # Look for email/phone in subsequent lines
                    for j in range(i + 2, min(i + 5, len(lines))):
                        line_content = lines[j].strip()
                        if '@' in line_content and not email:
                            email = line_content
                        elif any(char.isdigit() for char in line_content) and not phone:
                            phone = line_content
                    break
        
        # Fallback values if still empty
        if not name:
            name = 'Your Name'
        if not email:
            email = 'your.email@example.com'
        if not phone:
            phone = ''
        
        # Load template
        env = Environment(loader=FileSystemLoader('Template'))
        template = env.get_template('cover_letter_template.html')
        
        # Render template with data
        html_content = template.render(
            cover_letter_text=cover_letter_text,
            name=name,
            email=email,
            phone=phone
        )
        
        # Generate PDF
        pdf_buffer = HTML(string=html_content).write_pdf()
        
        # Return PDF as response
        return Response(
            content=pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cover_letter_{user_id}.pdf"}
        )
        
    except Exception as e:
        print(f"Error exporting cover letter PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to export cover letter PDF")

@app.post("/generate-resume-pdf")
async def generate_resume_pdf(resume_data: FinalResume, current_user = Depends(get_current_user)):
    """Generate PDF from resume data"""
    user_id = current_user.id
    
    try:
        # Load template
        env = Environment(loader=FileSystemLoader('Template'))
        template = env.get_template('resume_template.html')
        
        # Render template with data
        html_content = template.render(**resume_data.dict())
        
        # Generate PDF
        pdf_buffer = HTML(string=html_content).write_pdf()
        
        # Save to database
        title = f"Resume PDF - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        save_document_to_db(user_id, "resume", title, resume_data.dict())
        
        # Return PDF as response
        return Response(
            content=pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resume_{user_id}.pdf"}
        )
        
    except Exception as e:
        print(f"Error generating resume PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate resume PDF")

@app.post("/generate-cover-letter-pdf")
async def generate_cover_letter_pdf(request: CoverLetterPDFRequest, current_user = Depends(get_current_user)):
    """Generate PDF from cover letter data"""
    user_id = current_user.id
    
    try:
        # Load template
        env = Environment(loader=FileSystemLoader('Template'))
        template = env.get_template('cover_letter_template.html')
        
        # Render template with data
        html_content = template.render(
            cover_letter_text=request.cover_letter_text,
            name=request.user_name,
            email=request.user_email,
            phone=request.user_phone
        )
        
        # Generate PDF
        pdf_buffer = HTML(string=html_content).write_pdf()
        
        # Save to database
        title = f"Cover Letter PDF - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        save_document_to_db(user_id, "cover_letter", title, None, request.cover_letter_text)
        
        # Return PDF as response
        return Response(
            content=pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cover_letter_{user_id}.pdf"}
        )
        
    except Exception as e:
        print(f"Error generating cover letter PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cover letter PDF")

# --- PDF Upload and Processing ---

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """Upload and process PDF file"""
    user_id = current_user.id
    
    if not fitz:
        raise HTTPException(status_code=500, detail="PDF processing not available")
    
    try:
        # Read PDF content
        pdf_content = await file.read()
        
        # Extract text using PyMuPDF
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        return {"extracted_text": text}
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to process PDF")

# --- Static Files ---
# Only mount static files if the directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("Static files directory mounted successfully!")
else:
    print("Warning: Static directory not found. Static file serving disabled.")

# --- Main Application ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
