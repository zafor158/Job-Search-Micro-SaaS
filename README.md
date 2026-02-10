# Job Search Micro-SaaS

A comprehensive job search management platform built with FastAPI, Supabase, and modern web technologies. Track job applications, manage documents, and optimize your resume with AI-powered tools.

## Features

- 🔐 **User Authentication** - Secure login/signup with Supabase
- 📊 **Job Application Tracking** - Manage and monitor job applications
- 📄 **Document Management** - Store and organize resumes and cover letters
- 🤖 **AI Resume Optimization** - ATS-friendly resume optimization using Groq AI
- 📈 **Dashboard Analytics** - Track application progress and success rates
- 🎨 **Modern UI** - Professional, responsive design

## System UI/UX
<img width="1919" height="907" alt="image" src="https://github.com/user-attachments/assets/afc60357-e6a9-4f31-a515-4b8c90ba6f66" />
<img width="1919" height="917" alt="image" src="https://github.com/user-attachments/assets/95f75cdb-af0f-47dd-9b7a-e93d0b310f72" />
<img width="1919" height="917" alt="image" src="https://github.com/user-attachments/assets/5a0b8a5a-8393-4288-80c3-4258262af2b5" />
<img width="1918" height="909" alt="image" src="https://github.com/user-attachments/assets/dc99952d-cfe9-4eba-941f-2c1a62f71372" />
<img width="1919" height="904" alt="image" src="https://github.com/user-attachments/assets/17a79e8f-97fc-4642-8435-442dcc7a4e2e" />
<img width="1918" height="911" alt="image" src="https://github.com/user-attachments/assets/c2ff3618-c749-4878-b93a-bc6bd8b35ef4" />
<img width="1919" height="908" alt="image" src="https://github.com/user-attachments/assets/9d2c321f-4572-43b6-9e4b-65e959d11583" />








## Tech Stack

- **Backend**: FastAPI, Python
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **AI Services**: Groq API
- **Job APIs**: Adzuna, JSearch (optional)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/zafor158/Job-Search-Micro-SaaS.git
cd Job-Search-Micro-SaaS
```

### 2. Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Fill in your actual values in `.env`:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# AI Services
GROQ_API_KEY=your_groq_api_key_here

# Job Search APIs (Optional)
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_API_KEY=your_adzuna_api_key_here
JSEARCH_API_KEY=your_jsearch_api_key_here
```

### 3. Database Setup

Run the database setup scripts in order:
```bash
# Execute SQL files in sequence (00-07)
# These will create tables, indexes, functions, triggers, and sample data
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python start_server.py
```

The application will be available at `http://localhost:8000`

## Deployment

### Vercel Deployment (Recommended)

This project is configured for easy deployment on Vercel:

1. **Push to GitHub**: Ensure your code is pushed to GitHub
2. **Connect to Vercel**: Import your repository at [vercel.com](https://vercel.com)
3. **Set Environment Variables**: Add all variables from `.env.example`
4. **Deploy**: Click deploy and your app will be live!

For detailed deployment instructions, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

### Other Deployment Options

- **Railway**: Good for full-stack apps with databases
- **Render**: Alternative to Vercel with database support
- **DigitalOcean App Platform**: Full control over deployment

## Project Structure

```
Job-Search-Micro-SaaS/
├── api/                      # Vercel serverless functions
│   ├── main.py              # Vercel entry point
│   └── index.py             # Alternative handler
├── vercel.json              # Vercel configuration
├── VERCEL_DEPLOYMENT.md     # Detailed deployment guide
├── 00_complete_setup.sql    # Complete database setup
├── 01_create_tables.sql     # Database tables
├── 02_create_indexes.sql    # Database indexes
├── 03_create_functions.sql  # Database functions
├── 04_create_triggers.sql   # Database triggers
├── 05_create_rls_policies.sql # Row Level Security policies
├── 06_sample_data.sql       # Sample data
├── 07_verification_queries.sql # Verification queries
├── main.py                  # FastAPI application
├── services.py              # Business logic services
├── start_server.py          # Server startup script
├── ats_optimizer.py         # AI resume optimization
├── auth.html                # Login/signup page
├── indexnew.html            # Main application interface
├── Template/                # Resume and cover letter templates
├── data/profiles/           # Sample user profiles
├── .env.example             # Environment variables template
└── requirements.txt         # Python dependencies
```

## API Endpoints

- `POST /signup` - User registration
- `POST /token` - User login
- `GET /dashboard` - User dashboard data
- `GET /applications` - Get job applications
- `POST /applications` - Create new job application
- `GET /documents` - Get user documents
- `POST /documents` - Upload document
- `POST /optimize-resume` - AI resume optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
