# Vercel entry point for Job Search Micro-SaaS
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import the main FastAPI app
from main import app

# This is the handler that Vercel will use
def handler(request):
    return app(request.scope, request.receive, request.send)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
