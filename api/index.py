from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from main import app as fastapi_app

# Create a new FastAPI instance for Vercel
app = FastAPI(title="Job Search Micro-SaaS API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes from main.py
app.include_router(fastapi_app.router)

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML files
@app.get("/")
async def serve_index():
    return FileResponse("indexnew.html")

@app.get("/auth")
async def serve_auth():
    return FileResponse("auth.html")

# This is the main handler for Vercel
def handler(request):
    return app(request.scope, request.receive, request.send)
