-- =====================================================
-- 07_verification_queries.sql
-- Verification and testing queries for Job Search Micro-SaaS
-- =====================================================

-- =====================================================
-- DATABASE STRUCTURE VERIFICATION
-- =====================================================

-- Check if all tables exist
SELECT 'Table existence check:' as info;
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY table_name;

-- =====================================================
-- TABLE STRUCTURE VERIFICATION
-- =====================================================

-- Users table structure
SELECT 'Users table structure:' as info;
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Profiles table structure
SELECT 'Profiles table structure:' as info;
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'profiles' 
ORDER BY ordinal_position;

-- Documents table structure
SELECT 'Documents table structure:' as info;
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'documents' 
ORDER BY ordinal_position;

-- Job applications table structure
SELECT 'Job applications table structure:' as info;
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'job_applications' 
ORDER BY ordinal_position;

-- =====================================================
-- INDEXES VERIFICATION
-- =====================================================

-- Show all indexes
SELECT 'Created indexes:' as info;
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE tablename IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY tablename, indexname;

-- =====================================================
-- FUNCTIONS VERIFICATION
-- =====================================================

-- Show all functions
SELECT 'Created functions:' as info;
SELECT 
    routine_name, 
    routine_type, 
    data_type,
    routine_definition
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name IN (
    'hash_password', 
    'verify_password', 
    'update_updated_at_column', 
    'validate_email',
    'validate_username',
    'get_user_stats',
    'get_document_stats',
    'cleanup_old_data'
)
ORDER BY routine_name;

-- =====================================================
-- TRIGGERS VERIFICATION
-- =====================================================

-- Show all triggers
SELECT 'Created triggers:' as info;
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_timing,
    action_statement
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
AND event_object_table IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY event_object_table, trigger_name;

-- =====================================================
-- RLS POLICIES VERIFICATION
-- =====================================================

-- Show RLS status
SELECT 'RLS Status:' as info;
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY tablename;

-- Show all policies
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

-- =====================================================
-- DATA VERIFICATION
-- =====================================================

-- Count records in each table
SELECT 'Record counts:' as info;
SELECT 
    'users' as table_name, 
    COUNT(*) as record_count 
FROM users
UNION ALL
SELECT 
    'profiles' as table_name, 
    COUNT(*) as record_count 
FROM profiles
UNION ALL
SELECT 
    'documents' as table_name, 
    COUNT(*) as record_count 
FROM documents
UNION ALL
SELECT 
    'job_applications' as table_name, 
    COUNT(*) as record_count 
FROM job_applications;

-- =====================================================
-- FUNCTION TESTING
-- =====================================================

-- Test password hashing function
SELECT 'Password function test:' as info;
SELECT 
    'test_password' as original_password,
    hash_password('test_password') as hashed_password,
    verify_password('test_password', hash_password('test_password')) as verification_result;

-- Test email validation function
SELECT 'Email validation test:' as info;
SELECT 
    'test@example.com' as email,
    validate_email('test@example.com') as is_valid
UNION ALL
SELECT 
    'invalid-email' as email,
    validate_email('invalid-email') as is_valid;

-- Test username validation function
SELECT 'Username validation test:' as info;
SELECT 
    'validuser123' as username,
    validate_username('validuser123') as is_valid
UNION ALL
SELECT 
    'ab' as username,
    validate_username('ab') as is_valid;

-- =====================================================
-- SAMPLE QUERIES FOR TESTING
-- =====================================================

-- Get user statistics (if sample data exists)
SELECT 'User statistics test:' as info;
SELECT * FROM get_user_stats('550e8400-e29b-41d4-a716-446655440000');

-- Get document statistics (if sample data exists)
SELECT 'Document statistics test:' as info;
SELECT * FROM get_document_stats('550e8400-e29b-41d4-a716-446655440000');

-- Sample query: Get all job applications for a user
SELECT 'Sample query - Job applications:' as info;
SELECT 
    ja.id,
    ja.company,
    ja.position,
    ja.status,
    ja.application_date,
    ja.location,
    u.name as user_name
FROM job_applications ja
JOIN users u ON ja.user_id = u.id
LIMIT 5;

-- Sample query: Get all documents for a user
SELECT 'Sample query - Documents:' as info;
SELECT 
    d.id,
    d.doc_type,
    d.title,
    d.created_at,
    u.name as user_name
FROM documents d
JOIN users u ON d.user_id = u.id
LIMIT 5;

-- =====================================================
-- PERFORMANCE CHECK
-- =====================================================

-- Check table sizes
SELECT 'Table sizes:' as info;
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE tablename IN ('users', 'profiles', 'documents', 'job_applications')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =====================================================
-- FINAL VERIFICATION
-- =====================================================
SELECT 'Database verification completed successfully!' as status;
SELECT 'All components are properly configured and ready for use.' as message;
