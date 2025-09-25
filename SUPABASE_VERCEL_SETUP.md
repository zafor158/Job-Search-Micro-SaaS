# Supabase + Vercel Connection Checklist

## ✅ Pre-Deployment Checklist

### 1. Supabase Project Setup
- [ ] Database tables created (run SQL scripts 00-07)
- [ ] Row Level Security (RLS) policies enabled
- [ ] Authentication providers configured
- [ ] API keys copied and ready

### 2. Vercel Environment Variables
- [ ] `SUPABASE_URL` added
- [ ] `SUPABASE_ANON_KEY` added
- [ ] `SUPABASE_SERVICE_ROLE_KEY` added
- [ ] `GROQ_API_KEY` added
- [ ] `ADZUNA_APP_ID` added
- [ ] `ADZUNA_API_KEY` added
- [ ] `JSEARCH_API_KEY` added
- [ ] `ALLOWED_ORIGINS` added (optional)

### 3. Supabase Authentication Settings
- [ ] Site URL updated to Vercel domain
- [ ] Redirect URLs configured
- [ ] CORS origins updated
- [ ] Email templates customized (optional)

## 🚀 Deployment Steps

### Step 1: Deploy to Vercel
1. Push your code to GitHub
2. Connect repository to Vercel
3. Add environment variables
4. Deploy

### Step 2: Update Supabase Settings
1. Get your Vercel domain (e.g., `https://your-app.vercel.app`)
2. Update Supabase Site URL
3. Add redirect URLs
4. Update CORS origins

### Step 3: Test Connection
1. Visit your Vercel app
2. Try to sign up/login
3. Test API endpoints
4. Check Vercel function logs

## 🔧 Troubleshooting

### Common Issues:

**1. CORS Errors**
- Solution: Update `ALLOWED_ORIGINS` in Vercel environment variables
- Add: `https://your-app.vercel.app`

**2. Authentication Not Working**
- Check Supabase Site URL matches Vercel domain
- Verify redirect URLs are correct
- Check API keys in Vercel environment variables

**3. Database Connection Issues**
- Verify Supabase URL and keys are correct
- Check if RLS policies allow your operations
- Test database queries in Supabase dashboard

**4. Environment Variables Not Loading**
- Ensure variables are set for Production environment
- Check variable names match exactly
- Redeploy after adding new variables

## 📋 Environment Variables Reference

```bash
# Required for Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Optional for AI features
GROQ_API_KEY=your_groq_key_here

# Optional for job search APIs
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_key
JSEARCH_API_KEY=your_jsearch_key

# Optional for CORS (comma-separated)
ALLOWED_ORIGINS=https://your-app.vercel.app,https://localhost:3000
```

## 🎯 Post-Deployment Verification

1. **Test Authentication**
   - Sign up with a new account
   - Login with existing account
   - Check user creation in Supabase dashboard

2. **Test API Endpoints**
   - `/api/dashboard` - Should return user data
   - `/api/applications` - Should return job applications
   - `/api/documents` - Should return user documents

3. **Test Database Operations**
   - Create a job application
   - Upload a document
   - Check data appears in Supabase dashboard

4. **Monitor Performance**
   - Check Vercel function logs
   - Monitor Supabase usage
   - Test cold start performance

## 📞 Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Supabase Auth Guide](https://supabase.com/docs/guides/auth)
