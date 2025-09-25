# Database Setup for Job Search Micro-SaaS

This directory contains all the SQL files needed to set up the database for your Job Search Micro-SaaS application.

## 📁 File Structure

```
database/
├── 00_complete_setup.sql      # Master file - runs all setup files
├── 01_create_tables.sql       # Core table creation
├── 02_create_indexes.sql      # Performance indexes
├── 03_create_functions.sql    # Helper functions
├── 04_create_triggers.sql     # Automatic timestamp updates
├── 05_create_rls_policies.sql # Row Level Security policies
├── 06_sample_data.sql         # Sample data for testing
├── 07_verification_queries.sql # Verification and testing queries
└── README_DATABASE.md         # This file
```

## 🚀 Quick Setup

### Option 1: Complete Setup (Recommended)
Run the master file to set up everything:
```sql
\i 00_complete_setup.sql
```

### Option 2: Step-by-Step Setup
Run files individually in order:
```sql
\i 01_create_tables.sql
\i 02_create_indexes.sql
\i 03_create_functions.sql
\i 04_create_triggers.sql
\i 05_create_rls_policies.sql
\i 06_sample_data.sql  -- Optional
\i 07_verification_queries.sql
```

## 📊 Database Schema

### Core Tables

1. **users** - User authentication and basic info
   - `id` (UUID, Primary Key)
   - `email` (TEXT, Unique)
   - `password_hash` (TEXT)
   - `name`, `phone`, `username`
   - `is_active`, `email_verified`
   - `created_at`, `updated_at`

2. **profiles** - Extended user profile data
   - `id` (UUID, Primary Key)
   - `email` (TEXT, Unique)
   - `name`, `phone`, `username`
   - `default_experience`, `default_skills`
   - `default_education`, `default_projects`
   - `created_at`, `updated_at`

3. **documents** - Resume and cover letter storage
   - `id` (UUID, Primary Key)
   - `user_id` (UUID, Foreign Key)
   - `doc_type` (TEXT: 'resume' or 'cover_letter')
   - `title` (TEXT)
   - `content_json` (JSONB)
   - `content_text` (TEXT)
   - `created_at`, `updated_at`

4. **job_applications** - Job application tracking
   - `id` (UUID, Primary Key)
   - `user_id` (UUID, Foreign Key)
   - `company`, `position` (TEXT)
   - `status` (TEXT: 'applied', 'interview', 'offer', 'rejected', 'withdrawn')
   - `application_date`, `deadline` (DATE)
   - `notes`, `job_description`, `salary_range`
   - `location`, `job_url`
   - `created_at`, `updated_at`

## 🔧 Features

### Security
- **Row Level Security (RLS)** enabled on all tables
- **Password hashing** using bcrypt
- **Email and username validation** functions

### Performance
- **Strategic indexes** on frequently queried columns
- **Composite indexes** for complex queries
- **Automatic timestamp updates** via triggers

### Helper Functions
- `hash_password(password)` - Hash passwords securely
- `verify_password(password, hash)` - Verify passwords
- `validate_email(email)` - Validate email format
- `validate_username(username)` - Validate username format
- `get_user_stats(user_id)` - Get user statistics
- `get_document_stats(user_id)` - Get document statistics
- `cleanup_old_data()` - Maintenance function

## 🧪 Testing

### Sample Data
The `06_sample_data.sql` file includes:
- 3 sample users with different roles
- Sample profiles with realistic data
- Sample documents (resumes and cover letters)
- Sample job applications with various statuses

### Verification
The `07_verification_queries.sql` file provides:
- Database structure verification
- Function testing
- Sample queries
- Performance checks

## 🔄 Maintenance

### Regular Tasks
1. **Monitor performance** using the verification queries
2. **Clean up old data** using the cleanup function (when enabled)
3. **Backup database** regularly
4. **Update indexes** as needed based on query patterns

### Backup Commands
```bash
# Backup entire database
pg_dump your_database_name > backup.sql

# Backup specific tables
pg_dump -t users -t profiles -t documents -t job_applications your_database_name > tables_backup.sql
```

## 🚨 Important Notes

1. **Extensions Required**: The setup requires `uuid-ossp` and `pgcrypto` extensions
2. **RLS Policies**: All tables have permissive RLS policies - adjust as needed for production
3. **Sample Data**: Remove sample data before production deployment
4. **Cleanup Function**: The cleanup function is disabled by default for safety
5. **Password Security**: Always use the provided password hashing functions

## 🔗 Integration

This database schema is designed to work with:
- **FastAPI backend** (main.py)
- **Supabase** as the database provider
- **JWT authentication** for user sessions
- **Row Level Security** for data isolation

## 📞 Support

If you encounter any issues:
1. Check the verification queries for errors
2. Ensure all extensions are installed
3. Verify Supabase connection settings
4. Check RLS policies if data access is restricted

---

**Happy coding! 🎉**
