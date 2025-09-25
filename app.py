# Simple FastAPI app for Vercel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

app = FastAPI(title="Job Search Micro-SaaS")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Job Search Micro-SaaS API is running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/test")
async def test():
    return {"message": "API is working!", "status": "success"}

@app.get("/auth", response_class=HTMLResponse)
async def auth():
    try:
        with open("auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Auth page not found</h1>", status_code=404)

@app.get("/index", response_class=HTMLResponse)
async def index():
    try:
        with open("indexnew.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Main page not found</h1>", status_code=404)

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
