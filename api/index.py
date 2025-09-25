# Ultra-minimal Vercel handler to avoid issubclass error
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

# Create FastAPI app
app = FastAPI(title="Job Search Micro-SaaS API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Job Search Micro-SaaS API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/test")
async def test():
    return JSONResponse(
        content={
            "message": "API is working!",
            "status": "success",
            "version": "1.0.0",
            "features": {
                "database": "not_available",
                "ai": "not_available",
                "basic_api": "working"
            }
        }
    )

# Serve static HTML files
@app.get("/auth", response_class=HTMLResponse)
async def serve_auth():
    try:
        with open("auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Auth page not found</h1>", status_code=404)

@app.get("/index", response_class=HTMLResponse)
async def serve_index():
    try:
        with open("indexnew.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Main page not found</h1>", status_code=404)

# Basic API endpoints (without database)
@app.post("/api/signup")
async def signup():
    return JSONResponse(
        content={"error": "Database not available. Please add Supabase package."},
        status_code=503
    )

@app.post("/api/token")
async def login():
    return JSONResponse(
        content={"error": "Database not available. Please add Supabase package."},
        status_code=503
    )

@app.get("/api/dashboard")
async def dashboard():
    return JSONResponse(
        content={"error": "Database not available. Please add Supabase package."},
        status_code=503
    )

@app.get("/api/applications")
async def applications():
    return JSONResponse(
        content={"error": "Database not available. Please add Supabase package."},
        status_code=503
    )

@app.get("/api/documents")
async def documents():
    return JSONResponse(
        content={"error": "Database not available. Please add Supabase package."},
        status_code=503
    )

# Simple handler for Vercel
def handler(request):
    return app(request.scope, request.receive, request.send)