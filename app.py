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
