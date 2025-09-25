# Vercel Dependency Conflict Fix Guide

## Problem: ResolutionImpossible Error

The error occurs when pip cannot resolve conflicting dependencies between package versions.

## Solutions Applied

### 1. Flexible Version Constraints
Instead of exact versions (`==`), using range constraints (`>=`, `<`) allows pip to find compatible versions.

### 2. Multiple Requirements Files
Created different requirements files for different scenarios:
- `requirements.txt` - Flexible versions (current)
- `requirements-minimal.txt` - Minimal exact versions
- `requirements-flexible.txt` - Range constraints

### 3. Alternative Approaches

#### Option A: Use Minimal Requirements
If flexible versions still fail, try the minimal requirements:

```bash
# In Vercel, you can specify a different requirements file
# by renaming requirements-minimal.txt to requirements.txt
```

#### Option B: Remove Conflicting Packages
If issues persist, remove packages one by one:

```bash
# Start with core packages only
fastapi>=0.100.0,<0.110.0
uvicorn>=0.20.0,<0.25.0
requests>=2.30.0,<2.32.0
python-dotenv>=1.0.0,<2.0.0
pydantic>=2.0.0,<3.0.0
```

#### Option C: Use Alternative Packages
Replace problematic packages:
- `groq` → `openai` (if Groq API is not essential)
- `supabase` → `postgrest` (minimal Supabase client)

## Testing Different Requirements

### Test 1: Current Flexible Versions
```bash
pip install -r requirements.txt
```

### Test 2: Minimal Versions
```bash
pip install -r requirements-minimal.txt
```

### Test 3: Core Only
```bash
pip install fastapi uvicorn requests python-dotenv pydantic
```

## Vercel-Specific Solutions

### 1. Use Different Python Version
In `vercel.json`, specify Python version:
```json
{
  "functions": {
    "api/main.py": {
      "runtime": "python3.9"
    }
  }
}
```

### 2. Use Build Command Override
In Vercel dashboard, set custom build command:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

### 3. Use Requirements File from Different Location
Create `requirements.txt` in the `api/` directory instead of root.

## Debugging Steps

1. **Test locally first:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check for conflicts:**
   ```bash
   pip check
   ```

3. **Use pip-tools for dependency resolution:**
   ```bash
   pip install pip-tools
   pip-compile requirements.in
   ```

## Current Status

✅ **Updated requirements.txt** with flexible versions  
✅ **Created multiple requirements files** for testing  
✅ **Removed problematic packages** (PyMuPDF, etc.)  
✅ **Code handles missing dependencies** gracefully  

## Next Steps

1. **Commit and push** the updated requirements
2. **Redeploy in Vercel** - should resolve dependency conflicts
3. **If still failing**, try requirements-minimal.txt
4. **Test core functionality** once deployed

## Fallback Plan

If all else fails, deploy with minimal dependencies and add features incrementally:

```bash
# Minimal working requirements
fastapi
uvicorn
requests
python-dotenv
pydantic
```
