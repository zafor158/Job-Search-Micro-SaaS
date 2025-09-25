-- =====================================================
-- 03_create_functions.sql
-- Helper functions for Job Search Micro-SaaS
-- =====================================================

-- =====================================================
-- PASSWORD FUNCTIONS
-- =====================================================

-- Function to hash passwords using bcrypt
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Use PostgreSQL's built-in crypt function with bcrypt
    RETURN crypt(password, gen_salt('bf'));
END;
$$ LANGUAGE plpgsql;

-- Function to verify passwords
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TIMESTAMP FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VALIDATION FUNCTIONS
-- =====================================================

-- Function to validate email format
CREATE OR REPLACE FUNCTION validate_email(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE plpgsql;

-- Function to validate username format
CREATE OR REPLACE FUNCTION validate_username(username TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Username should be 3-20 characters, alphanumeric and underscores only
    RETURN username ~* '^[a-zA-Z0-9_]{3,20}$';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- STATISTICS FUNCTIONS
-- =====================================================

-- Function to get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(user_uuid UUID)
RETURNS TABLE(
    total_applications BIGINT,
    total_documents BIGINT,
    recent_applications BIGINT,
    recent_documents BIGINT,
    applications_by_status JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM job_applications WHERE user_id = user_uuid) as total_applications,
        (SELECT COUNT(*) FROM documents WHERE user_id = user_uuid) as total_documents,
        (SELECT COUNT(*) FROM job_applications WHERE user_id = user_uuid AND application_date >= CURRENT_DATE - INTERVAL '30 days') as recent_applications,
        (SELECT COUNT(*) FROM documents WHERE user_id = user_uuid AND created_at >= NOW() - INTERVAL '30 days') as recent_documents,
        (SELECT jsonb_object_agg(status, count) FROM (
            SELECT status, COUNT(*) as count 
            FROM job_applications 
            WHERE user_id = user_uuid 
            GROUP BY status
        ) as status_counts) as applications_by_status;
END;
$$ LANGUAGE plpgsql;

-- Function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats(user_uuid UUID)
RETURNS TABLE(
    total_resumes BIGINT,
    total_cover_letters BIGINT,
    recent_resumes BIGINT,
    recent_cover_letters BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM documents WHERE user_id = user_uuid AND doc_type = 'resume') as total_resumes,
        (SELECT COUNT(*) FROM documents WHERE user_id = user_uuid AND doc_type = 'cover_letter') as total_cover_letters,
        (SELECT COUNT(*) FROM documents WHERE user_id = user_uuid AND doc_type = 'resume' AND created_at >= NOW() - INTERVAL '30 days') as recent_resumes,
        (SELECT COUNT(*) FROM documents WHERE user_id = user_uuid AND doc_type = 'cover_letter' AND created_at >= NOW() - INTERVAL '30 days') as recent_cover_letters;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MAINTENANCE FUNCTIONS
-- =====================================================

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS TABLE(
    deleted_documents BIGINT,
    deleted_applications BIGINT
) AS $$
DECLARE
    doc_count BIGINT;
    app_count BIGINT;
BEGIN
    -- Delete documents older than 1 year (optional - commented out for safety)
    -- DELETE FROM documents WHERE created_at < NOW() - INTERVAL '1 year';
    -- GET DIAGNOSTICS doc_count = ROW_COUNT;
    
    -- Delete job applications older than 2 years (optional - commented out for safety)
    -- DELETE FROM job_applications WHERE created_at < NOW() - INTERVAL '2 years';
    -- GET DIAGNOSTICS app_count = ROW_COUNT;
    
    -- For now, just return 0 counts since cleanup is disabled
    doc_count := 0;
    app_count := 0;
    
    RETURN QUERY SELECT doc_count, app_count;
    
    RAISE NOTICE 'Cleanup function executed successfully (cleanup disabled for safety)';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'Functions created successfully!' as status;

-- Show created functions
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
