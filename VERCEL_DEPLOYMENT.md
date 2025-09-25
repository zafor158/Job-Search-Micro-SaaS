# Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your project should be pushed to GitHub
3. **Supabase Project**: Database should be set up and accessible

## Deployment Steps

### 1. Connect Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository: `zafor158/Job-Search-Micro-SaaS`
4. Vercel will automatically detect the Python project

### 2. Configure Environment Variables

In Vercel dashboard, go to your project settings and add these environment variables:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
GROQ_API_KEY=your_groq_api_key_here
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_API_KEY=your_adzuna_api_key_here
JSEARCH_API_KEY=your_jsearch_api_key_here
```

### 3. Configure Build Settings

- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### 4. Deploy

1. Click "Deploy" in Vercel dashboard
2. Wait for the build to complete
3. Your app will be available at `https://your-project-name.vercel.app`

## Project Structure for Vercel

```
Job-Search-Micro-SaaS/
├── api/
│   ├── main.py          # Vercel entry point
│   └── index.py         # Alternative handler
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies
├── main.py              # Main FastAPI application
├── services.py          # Business logic
├── auth.html            # Login page
├── indexnew.html        # Main app interface
└── [other files...]
```

## Important Notes

### Database Setup
- Run the SQL setup scripts (00-07) in your Supabase dashboard
- Ensure all tables, indexes, and functions are created
- Test database connectivity from Vercel

### File Limitations
- Vercel has file size limits for serverless functions
- Large files (PDFs, images) should be stored in Supabase Storage
- Consider using Supabase Storage for document uploads

### Cold Starts
- First request might be slower due to cold start
- Consider upgrading to Vercel Pro for better performance
- Use connection pooling for database connections

### CORS Configuration
- Update CORS settings in `main.py` for your Vercel domain
- Replace `allow_origins=["*"]` with your actual domain

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements.txt`
2. **Environment Variables**: Double-check all variables are set in Vercel
3. **Database Connection**: Verify Supabase URL and keys are correct
4. **File Uploads**: Use Supabase Storage for file handling

### Debugging

1. Check Vercel function logs in dashboard
2. Use `print()` statements for debugging (visible in logs)
3. Test API endpoints individually
4. Verify database queries work in Supabase dashboard

## Production Considerations

1. **Security**: Update CORS origins to your domain only
2. **Rate Limiting**: Implement rate limiting for API endpoints
3. **Error Handling**: Add proper error handling and logging
4. **Monitoring**: Set up monitoring and alerts
5. **Backup**: Regular database backups

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Supabase Documentation](https://supabase.com/docs)
