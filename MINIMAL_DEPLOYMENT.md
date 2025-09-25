# Minimal Vercel Deployment Guide

## Current Status: Core-Only Version

Due to dependency conflicts, we've deployed a minimal version with core functionality only.

## What's Working ✅

- **FastAPI Application** - Basic web server
- **Authentication Endpoints** - Login/signup (without database)
- **Static File Serving** - HTML pages
- **CORS Configuration** - Cross-origin requests
- **Basic API Structure** - All endpoints defined

## What's Limited ⚠️

- **Database Operations** - Supabase client not available
- **AI Features** - Groq API not available
- **File Processing** - Limited to basic operations

## Current Requirements

```bash
fastapi>=0.100.0,<0.110.0
uvicorn>=0.20.0,<0.25.0
requests>=2.30.0,<2.32.0
python-dotenv>=1.0.0,<2.0.0
pydantic>=2.0.0,<3.0.0
jinja2>=3.1.0,<3.2.0
httpx>=0.25.0,<0.26.0
```

## Deployment Steps

1. **Deploy to Vercel** - Should build successfully now
2. **Add Environment Variables** (optional for core version):
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_key
   GROQ_API_KEY=your_groq_key
   ```
3. **Test Basic Functionality** - App should load and serve pages

## Testing Your Deployment

### Basic Tests
- Visit your Vercel URL - should show the main page
- Check `/docs` endpoint - should show FastAPI documentation
- Test CORS - should allow cross-origin requests

### API Endpoints (Limited Functionality)
- `GET /` - Main page
- `GET /auth` - Login page
- `POST /api/signup` - Will return error (no database)
- `POST /api/token` - Will return error (no database)

## Next Steps: Adding Features Back

### Step 1: Add Supabase (Database)
```bash
# Add to requirements.txt
supabase>=2.0.0,<2.1.0
```

### Step 2: Add Groq (AI Features)
```bash
# Add to requirements.txt
groq>=0.4.0,<0.5.0
```

### Step 3: Test Each Addition
Add packages one by one and test deployment:
1. Deploy with Supabase only
2. Deploy with Groq only
3. Deploy with both

## Alternative Approaches

### Option 1: Separate Services
- Deploy core app to Vercel
- Deploy database operations to Railway/Render
- Deploy AI features to separate service

### Option 2: Use Different Packages
- Replace `supabase` with `postgrest` (minimal client)
- Replace `groq` with `openai` (more stable)

### Option 3: Manual Installation
- Use Vercel's build command override
- Install packages manually in build process

## Current Error Handling

The app gracefully handles missing packages:
- **Supabase**: Returns helpful error messages
- **Groq**: Returns 503 error with installation instructions
- **Core Features**: Work normally

## Success Criteria

✅ **App deploys successfully**  
✅ **Basic pages load**  
✅ **API endpoints respond**  
✅ **No dependency conflicts**  
✅ **Ready for incremental feature addition**  

## Troubleshooting

If deployment still fails:
1. Check Vercel build logs
2. Try even more minimal requirements
3. Use Vercel's Python 3.9 runtime
4. Contact Vercel support for Python package issues
