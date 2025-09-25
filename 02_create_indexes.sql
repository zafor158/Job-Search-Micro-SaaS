-- =====================================================
-- 02_create_indexes.sql
-- Performance indexes for Job Search Micro-SaaS
-- =====================================================

-- =====================================================
-- USERS TABLE INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified);

-- =====================================================
-- PROFILES TABLE INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_updated_at ON profiles(updated_at);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles(created_at);

-- =====================================================
-- DOCUMENTS TABLE INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_user_type ON documents(user_id, doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);

-- =====================================================
-- JOB_APPLICATIONS TABLE INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_job_applications_application_date ON job_applications(application_date);
CREATE INDEX IF NOT EXISTS idx_job_applications_company ON job_applications(company);
CREATE INDEX IF NOT EXISTS idx_job_applications_position ON job_applications(position);
CREATE INDEX IF NOT EXISTS idx_job_applications_deadline ON job_applications(deadline);
CREATE INDEX IF NOT EXISTS idx_job_applications_user_status ON job_applications(user_id, status);

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'Indexes created successfully!' as status;

-- Show created indexes
SELECT 'Created indexes:' as info;
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE tablename IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY tablename, indexname;
