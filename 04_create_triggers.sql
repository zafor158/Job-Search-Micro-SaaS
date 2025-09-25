-- =====================================================
-- 04_create_triggers.sql
-- Triggers for automatic timestamp updates
-- =====================================================

-- =====================================================
-- USERS TABLE TRIGGERS
-- =====================================================

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- PROFILES TABLE TRIGGERS
-- =====================================================

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- DOCUMENTS TABLE TRIGGERS
-- =====================================================

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- JOB_APPLICATIONS TABLE TRIGGERS
-- =====================================================

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS update_job_applications_updated_at ON job_applications;

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_job_applications_updated_at
    BEFORE UPDATE ON job_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'Triggers created successfully!' as status;

-- Show created triggers
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
