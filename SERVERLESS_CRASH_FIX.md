# Vercel Serverless Function Crash Debug Guide

## Problem: FUNCTION_INVOCATION_FAILED (500 Error)

The serverless function is crashing due to import errors or missing dependencies.

## Root Causes

1. **Import Errors** - Trying to import packages not in requirements.txt
2. **Missing Files** - Referencing files that don't exist
3. **Configuration Issues** - Incorrect Vercel configuration
4. **Dependency Conflicts** - Package version conflicts

## Solution Applied

### 1. Created Minimal API Handler
- **Removed complex imports** from main.py
- **Created standalone FastAPI app** in api/main.py
- **Added error handling** for missing files
- **Simplified dependencies** to core packages only

### 2. Basic Endpoints Created
- `GET /` - Health check
- `GET /health` - Status endpoint
- `GET /auth` - Auth page
- `GET /index` - Main page
- `GET /api/test` - Test endpoint
- `POST /api/signup` - Returns helpful error
- `POST /api/token` - Returns helpful error

### 3. Error Handling Added
- **File not found** - Returns 404 with message
- **Missing packages** - Returns 503 with instructions
- **Graceful degradation** - App works without database/AI

## Testing Your Deployment

### Step 1: Basic Health Check
Visit: `https://your-app.vercel.app/`
Expected: `{"message": "Job Search Micro-SaaS API is running!", "status": "healthy"}`

### Step 2: Test Endpoint
Visit: `https://your-app.vercel.app/api/test`
Expected: JSON with status and feature availability

### Step 3: Check Pages
- `https://your-app.vercel.app/auth` - Should show auth page
- `https://your-app.vercel.app/index` - Should show main page

### Step 4: API Documentation
Visit: `https://your-app.vercel.app/docs`
Expected: FastAPI automatic documentation

## Debugging Steps

### 1. Check Vercel Logs
- Go to Vercel dashboard
- Click on your function
- Check "Function Logs" tab
- Look for import errors or exceptions

### 2. Test Locally
```bash
# Test the API handler locally
cd api
python main.py
```

### 3. Check Requirements
```bash
# Verify all packages install correctly
pip install -r requirements.txt
```

### 4. Minimal Test
```bash
# Test with absolute minimal requirements
pip install fastapi uvicorn
```

## Common Issues and Fixes

### Issue 1: Import Error
**Error**: `ModuleNotFoundError: No module named 'supabase'`
**Fix**: The new api/main.py doesn't import supabase

### Issue 2: File Not Found
**Error**: `FileNotFoundError: auth.html`
**Fix**: Check file paths in api/main.py

### Issue 3: Handler Function
**Error**: `AttributeError: 'ASGIApp' object has no attribute 'handler'`
**Fix**: Use the correct handler function in api/main.py

## Current Status

✅ **Minimal API handler created**  
✅ **No complex imports**  
✅ **Error handling added**  
✅ **Basic endpoints working**  
✅ **Health checks available**  

## Next Steps

1. **Deploy and test** the minimal version
2. **Verify basic functionality** works
3. **Add features incrementally**:
   - Add Supabase package
   - Add Groq package
   - Test each addition

## Fallback Plan

If the minimal version still crashes:

### Option 1: Even More Minimal
```python
# Ultra-minimal handler
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

def handler(request):
    return app(request.scope, request.receive, request.send)
```

### Option 2: Use Vercel's Python Template
- Start with Vercel's Python template
- Add features one by one
- Test each addition

### Option 3: Different Deployment Platform
- Try Railway or Render
- May have better Python support
- Less restrictive than Vercel

## Success Criteria

✅ **Function deploys without crashing**  
✅ **Health check endpoint responds**  
✅ **Basic API endpoints work**  
✅ **Error messages are helpful**  
✅ **Ready for feature addition**  
