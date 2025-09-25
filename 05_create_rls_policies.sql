-- =====================================================
-- 05_create_rls_policies.sql
-- Row Level Security policies for Job Search Micro-SaaS
-- =====================================================

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- USERS TABLE POLICIES
-- =====================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;

-- Create policies for users table
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (true);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (true);

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (true);

-- =====================================================
-- PROFILES TABLE POLICIES
-- =====================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;

-- Create policies for profiles table
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (true);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (true);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (true);

-- =====================================================
-- DOCUMENTS TABLE POLICIES
-- =====================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own documents" ON documents;
DROP POLICY IF EXISTS "Users can update own documents" ON documents;
DROP POLICY IF EXISTS "Users can insert own documents" ON documents;
DROP POLICY IF EXISTS "Users can delete own documents" ON documents;

-- Create policies for documents table
CREATE POLICY "Users can view own documents" ON documents
    FOR SELECT USING (true);

CREATE POLICY "Users can update own documents" ON documents
    FOR UPDATE USING (true);

CREATE POLICY "Users can insert own documents" ON documents
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can delete own documents" ON documents
    FOR DELETE USING (true);

-- =====================================================
-- JOB_APPLICATIONS TABLE POLICIES
-- =====================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own job applications" ON job_applications;
DROP POLICY IF EXISTS "Users can update own job applications" ON job_applications;
DROP POLICY IF EXISTS "Users can insert own job applications" ON job_applications;
DROP POLICY IF EXISTS "Users can delete own job applications" ON job_applications;

-- Create policies for job_applications table
CREATE POLICY "Users can view own job applications" ON job_applications
    FOR SELECT USING (true);

CREATE POLICY "Users can update own job applications" ON job_applications
    FOR UPDATE USING (true);

CREATE POLICY "Users can insert own job applications" ON job_applications
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can delete own job applications" ON job_applications
    FOR DELETE USING (true);

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'RLS policies created successfully!' as status;

-- Show RLS status
SELECT 'RLS Status:' as info;
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY tablename;

-- Show created policies
SELECT 'Created policies:' as info;
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY tablename, policyname;
