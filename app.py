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

# Main app interface - serve indexnew.html as the homepage
@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("indexnew.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Job Search Micro-SaaS</title></head>
        <body>
            <h1>Welcome to Job Search Micro-SaaS</h1>
            <p>Main interface not found. Please check file paths.</p>
            <a href="/auth">Go to Login</a>
        </body>
        </html>
        """, status_code=404)

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

# Main app page
@app.get("/index", response_class=HTMLResponse)
async def index():
    try:
        with open("indexnew.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>App - Job Search Micro-SaaS</title></head>
        <body>
            <h1>Main App</h1>
            <p>Main page not found. Please check file paths.</p>
            <a href="/">Go Home</a>
        </body>
        </html>
        """, status_code=404)

# API endpoints (without database)
@app.post("/api/signup")
async def signup():
    return JSONResponse(content={"error": "Database not available"}, status_code=503)

@app.post("/api/token")
async def token():
    return JSONResponse(content={"error": "Database not available"}, status_code=503)

@app.get("/api/dashboard")
async def dashboard():
    return JSONResponse(content={"error": "Database not available"}, status_code=503)

@app.get("/api/applications")
async def applications():
    return JSONResponse(content={"error": "Database not available"}, status_code=503)

@app.get("/api/documents")
async def documents():
    return JSONResponse(content={"error": "Database not available"}, status_code=503)
