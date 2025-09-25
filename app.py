# Simple FastAPI app for Vercel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Job Search Micro-SaaS")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if they exist
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Main app interface - redirect to login first
@app.get("/", response_class=HTMLResponse)
async def home():
    # Redirect to login page since users need to authenticate first
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
            }
            .btn:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Job Search Micro-SaaS</h1>
            <p>Welcome to your job search management platform. Please log in to access your dashboard and manage your applications.</p>
            <a href="/auth" class="btn">Log In / Sign Up</a>
        </div>
    </body>
    </html>
    """)

# API health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/test")
async def test():
    return {"message": "API is working!", "status": "success"}

# Auth page
@app.get("/auth", response_class=HTMLResponse)
async def auth():
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

# Dashboard route - main app interface
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
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

# API endpoints (without database)
@app.post("/api/logout")
async def logout():
    """Logout endpoint - clears token on client side"""
    return JSONResponse(content={"message": "Logged out successfully"})

@app.post("/api/signup")
async def signup():
    return JSONResponse(content={"message": "Signup successful", "access_token": "mock_token", "token_type": "bearer"})

@app.post("/api/token")
async def token():
    return JSONResponse(content={"message": "Login successful", "access_token": "mock_token", "token_type": "bearer"})

@app.get("/api/dashboard")
async def dashboard():
    return JSONResponse(content={"message": "Dashboard data loaded", "status": "success"})

# Profile endpoints
@app.get("/api/profile")
async def get_profile():
    """Get user profile from localStorage"""
    try:
        # In a real app, this would get the user from JWT token
        # For now, we'll return a mock profile or empty profile
        return JSONResponse(content={
            "email": "user@example.com",
            "name": "User Name",
            "username": "username",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "default_skills": "Python, JavaScript, React",
            "default_experience": "Software Developer with 5+ years experience",
            "default_education": "Bachelor's in Computer Science",
            "default_projects": "Built multiple web applications",
            "avatar_url": None
        })
    except Exception as e:
        return JSONResponse(content={"error": "Failed to fetch profile"}, status_code=500)

@app.put("/api/update-profile")
async def update_profile():
    """Update user profile"""
    try:
        # In a real app, this would update the database
        # For now, we'll return success
        return JSONResponse(content={
            "message": "Profile updated successfully",
            "email": "user@example.com",
            "name": "Updated Name",
            "username": "updated_username",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "default_skills": "Python, JavaScript, React, Node.js",
            "default_experience": "Senior Software Developer with 5+ years experience",
            "default_education": "Bachelor's in Computer Science",
            "default_projects": "Built multiple web applications and mobile apps",
            "avatar_url": None
        })
    except Exception as e:
        return JSONResponse(content={"error": "Failed to update profile"}, status_code=500)

# Resume Generation Endpoints
@app.post("/api/generate_resume")
async def generate_resume():
    """Generate resume"""
    return JSONResponse(content={
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1 (555) 123-4567",
        "summary": "Experienced software developer with 5+ years of expertise in Python, JavaScript, and full-stack development. Passionate about creating efficient solutions and leading development teams.",
        "experience": [
            {
                "title": "Senior Software Developer",
                "company": "Tech Solutions Inc",
                "dates": "2020 - Present",
                "bullets": [
                    "Led a team of 5 developers in building scalable web applications",
                    "Reduced application load time by 40% through code optimization",
                    "Implemented CI/CD pipelines improving deployment efficiency by 60%",
                    "Mentored junior developers and conducted code reviews"
                ]
            },
            {
                "title": "Software Developer",
                "company": "Digital Innovations",
                "dates": "2018 - 2020",
                "bullets": [
                    "Developed RESTful APIs using Python and FastAPI",
                    "Built responsive web applications with React and Node.js",
                    "Collaborated with cross-functional teams on product development",
                    "Maintained and updated legacy systems"
                ]
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "bullets": [
                    "Built full-stack e-commerce solution serving 10,000+ users",
                    "Implemented payment processing with Stripe API",
                    "Designed responsive UI with React and Material-UI",
                    "Achieved 99.9% uptime through robust error handling"
                ]
            },
            {
                "title": "Data Analytics Dashboard",
                "bullets": [
                    "Created real-time analytics dashboard using Python and D3.js",
                    "Processed large datasets with Pandas and NumPy",
                    "Implemented automated reporting system",
                    "Reduced manual reporting time by 80%"
                ]
            }
        ],
        "education": "Bachelor of Science in Computer Science, University of Technology (2014-2018)",
        "skills": ["Python", "JavaScript", "React", "Node.js", "FastAPI", "PostgreSQL", "Docker", "AWS", "Git", "Agile/Scrum"]
    })

@app.post("/api/generate_modified_resume")
async def generate_modified_resume():
    """Generate modified resume"""
    return JSONResponse(content={
        "name": "John Doe",
        "email": "john.doe@email.com", 
        "phone": "+1 (555) 123-4567",
        "summary": "Senior Software Developer with 6+ years of experience specializing in Python, JavaScript, and cloud technologies. Proven track record of leading development teams and delivering high-impact solutions.",
        "experience": [
            {
                "title": "Lead Software Developer",
                "company": "Tech Solutions Inc",
                "dates": "2021 - Present",
                "bullets": [
                    "Lead a team of 8 developers in building enterprise-scale applications",
                    "Architected microservices solution reducing system complexity by 50%",
                    "Implemented automated testing increasing code coverage to 95%",
                    "Mentored 3 junior developers and established coding standards"
                ]
            },
            {
                "title": "Senior Software Developer", 
                "company": "Digital Innovations",
                "dates": "2019 - 2021",
                "bullets": [
                    "Developed high-performance APIs handling 1M+ requests daily",
                    "Built real-time data processing pipeline using Python and Kafka",
                    "Led migration from monolithic to microservices architecture",
                    "Collaborated with DevOps team on containerization strategy"
                ]
            }
        ],
        "projects": [
            {
                "title": "Cloud-Native E-commerce Platform",
                "bullets": [
                    "Designed and built scalable e-commerce platform on AWS",
                    "Implemented auto-scaling and load balancing for 50,000+ concurrent users",
                    "Integrated payment processing with fraud detection",
                    "Achieved 99.99% uptime with comprehensive monitoring"
                ]
            },
            {
                "title": "AI-Powered Analytics Platform",
                "bullets": [
                    "Developed machine learning pipeline for predictive analytics",
                    "Built real-time dashboard with React and WebSocket connections",
                    "Implemented data visualization using D3.js and Chart.js",
                    "Reduced manual analysis time by 90% through automation"
                ]
            }
        ],
        "education": "Master of Science in Computer Science, University of Technology (2016-2018)\nBachelor of Science in Computer Science, University of Technology (2012-2016)",
        "skills": ["Python", "JavaScript", "React", "Node.js", "FastAPI", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Azure", "Git", "Agile/Scrum", "Machine Learning"]
    })

# Cover Letter Generation Endpoints
@app.post("/api/generate/cover-letter")
async def generate_cover_letter():
    """Generate cover letter"""
    return JSONResponse(content={
        "cover_letter_text": """Dear Hiring Manager,

I am writing to express my strong interest in the Software Developer position at your company. With over 5 years of experience in full-stack development and a passion for creating innovative solutions, I am confident that I would be a valuable addition to your team.

In my current role as Senior Software Developer at Tech Solutions Inc, I have successfully led development teams and delivered high-quality applications that serve thousands of users. My expertise spans across Python, JavaScript, React, and Node.js, with a particular strength in building scalable web applications and RESTful APIs.

Key highlights of my experience include:
• Led a team of 5 developers in building scalable web applications
• Reduced application load time by 40% through code optimization
• Implemented CI/CD pipelines improving deployment efficiency by 60%
• Built full-stack e-commerce solution serving 10,000+ users
• Created real-time analytics dashboard using Python and D3.js

I am particularly drawn to your company's commitment to innovation and excellence. I believe my technical skills, leadership experience, and passion for continuous learning align perfectly with your team's goals. I am excited about the opportunity to contribute to your projects and grow with your organization.

Thank you for considering my application. I would welcome the opportunity to discuss how my experience and skills can contribute to your team's success. I am available for an interview at your convenience.

Sincerely,
John Doe"""
    })

@app.post("/api/generate_matched_cover_letter")
async def generate_matched_cover_letter():
    """Generate matched cover letter"""
    return JSONResponse(content={
        "message": "Matched cover letter generated successfully",
        "cover_letter_text": "Sample matched cover letter content",
        "status": "success"
    })

# Job Search Endpoints
@app.post("/api/match_jobs")
async def match_jobs():
    """Match jobs"""
    return JSONResponse(content={
        "message": "Jobs matched successfully",
        "jobs": [
            {
                "title": "Software Developer",
                "company": "Tech Corp",
                "location": "Remote",
                "salary": "$80,000 - $120,000",
                "description": "Looking for an experienced software developer with Python and React skills",
                "url": "https://example.com/job/1",
                "match_percentage": 85
            },
            {
                "title": "Python Developer",
                "company": "Data Solutions",
                "location": "New York",
                "salary": "$90,000 - $130,000", 
                "description": "Senior Python developer position for data processing team",
                "url": "https://example.com/job/2",
                "match_percentage": 92
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "location": "San Francisco",
                "salary": "$100,000 - $150,000",
                "description": "Full stack developer with React and Node.js experience",
                "url": "https://example.com/job/3", 
                "match_percentage": 78
            }
        ],
        "status": "success"
    })

# Document Management Endpoints
@app.get("/api/documents")
async def get_documents():
    """Get user documents"""
    return JSONResponse(content=[
        {
            "id": "1",
            "name": "My Resume",
            "type": "resume",
            "created_at": "2024-01-01T00:00:00Z",
            "file_size": "245KB",
            "download_url": "/api/documents/1/pdf"
        },
        {
            "id": "2",
            "name": "Cover Letter - Tech Corp",
            "type": "cover_letter", 
            "created_at": "2024-01-15T00:00:00Z",
            "file_size": "89KB",
            "download_url": "/api/documents/2/pdf"
        },
        {
            "id": "3",
            "name": "Updated Resume v2",
            "type": "resume",
            "created_at": "2024-01-20T00:00:00Z", 
            "file_size": "267KB",
            "download_url": "/api/documents/3/pdf"
        }
    ])

@app.get("/api/documents/{doc_id}/pdf")
async def get_document_pdf(doc_id: str):
    """Get document PDF"""
    return JSONResponse(content={
        "message": f"PDF for document {doc_id} retrieved",
        "pdf_url": f"/api/documents/{doc_id}/pdf",
        "status": "success"
    })

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document"""
    return JSONResponse(content={
        "message": f"Document {doc_id} deleted successfully",
        "status": "success"
    })

# File Upload Endpoints
@app.post("/api/upload/pdf")
async def upload_pdf():
    """Upload PDF file"""
    return JSONResponse(content={
        "message": "PDF uploaded successfully",
        "file_id": "uploaded_file_123",
        "status": "success"
    })

@app.post("/api/avatar")
async def upload_avatar():
    """Upload avatar"""
    return JSONResponse(content={
        "message": "Avatar uploaded successfully",
        "avatar_url": "/api/avatar/uploaded_avatar.jpg",
        "status": "success"
    })

# Application Management Endpoints
@app.get("/api/applications")
async def get_applications():
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
        },
        {
            "id": "2", 
            "job_title": "Python Developer",
            "company": "Data Solutions",
            "location": "New York",
            "status": "Interview",
            "applied_date": "2024-01-15",
            "job_url": "https://example.com/job/2",
            "salary_range": "$90,000 - $130,000",
            "job_type": "Full-time",
            "job_description": "Senior Python developer position",
            "deadline": "2024-02-15"
        }
    ])

@app.post("/api/applications")
async def create_application():
    """Create new application"""
    return JSONResponse(content={
        "message": "Application created successfully",
        "application_id": "new_app_123",
        "status": "success"
    })

@app.put("/api/applications/{app_id}")
async def update_application(app_id: str):
    """Update application"""
    return JSONResponse(content={
        "message": f"Application {app_id} updated successfully",
        "status": "success"
    })

@app.delete("/api/applications/{app_id}")
async def delete_application(app_id: str):
    """Delete application"""
    return JSONResponse(content={
        "message": f"Application {app_id} deleted successfully",
        "status": "success"
    })

# Additional Endpoints
@app.post("/api/events")
async def log_event():
    """Log user event"""
    return JSONResponse(content={
        "message": "Event logged successfully",
        "status": "success"
    })

@app.post("/api/change-password")
async def change_password():
    """Change user password"""
    return JSONResponse(content={
        "message": "Password changed successfully",
        "status": "success"
    })

@app.post("/api/generate_interview_prep")
async def generate_interview_prep():
    """Generate interview preparation"""
    return JSONResponse(content={
        "message": "Interview prep generated successfully",
        "prep_content": "Sample interview preparation content",
        "status": "success"
    })
