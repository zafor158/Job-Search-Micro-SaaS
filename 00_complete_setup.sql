-- =====================================================
-- 00_complete_setup.sql
-- Complete database setup for Job Search Micro-SaaS
-- Run this file to set up the entire database
-- =====================================================

-- =====================================================
-- EXECUTION ORDER
-- =====================================================
-- This file executes all database setup files in the correct order:
-- 1. Create tables
-- 2. Create indexes
-- 3. Create functions
-- 4. Create triggers
-- 5. Create RLS policies
-- 6. Insert sample data (optional)
-- 7. Run verification queries

-- =====================================================
-- STEP 1: CREATE TABLES
-- =====================================================
\echo 'Step 1: Creating tables...'
\i 01_create_tables.sql

-- =====================================================
-- STEP 2: CREATE INDEXES
-- =====================================================
\echo 'Step 2: Creating indexes...'
\i 02_create_indexes.sql

-- =====================================================
-- STEP 3: CREATE FUNCTIONS
-- =====================================================
\echo 'Step 3: Creating functions...'
\i 03_create_functions.sql

-- =====================================================
-- STEP 4: CREATE TRIGGERS
-- =====================================================
\echo 'Step 4: Creating triggers...'
\i 04_create_triggers.sql

-- =====================================================
-- STEP 5: CREATE RLS POLICIES
-- =====================================================
\echo 'Step 5: Creating RLS policies...'
\i 05_create_rls_policies.sql

-- =====================================================
-- STEP 6: INSERT SAMPLE DATA (OPTIONAL)
-- =====================================================
-- Uncomment the following line if you want to insert sample data
-- \echo 'Step 6: Inserting sample data...'
-- \i 06_sample_data.sql

-- =====================================================
-- STEP 7: RUN VERIFICATION
-- =====================================================
\echo 'Step 7: Running verification queries...'
\i 07_verification_queries.sql

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================
\echo '====================================================='
\echo 'Database setup completed successfully!'
\echo 'Your Job Search Micro-SaaS database is ready to use.'
\echo '====================================================='
