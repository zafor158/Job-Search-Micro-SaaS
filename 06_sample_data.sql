-- =====================================================
-- 06_sample_data.sql
-- Sample data for testing Job Search Micro-SaaS
-- =====================================================

-- =====================================================
-- SAMPLE USERS
-- =====================================================

-- Insert sample users
INSERT INTO users (id, email, password_hash, name, phone, username, is_active, email_verified) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'john.doe@example.com', hash_password('password123'), 'John Doe', '+1234567890', 'johndoe', true, true),
('550e8400-e29b-41d4-a716-446655440001', 'jane.smith@example.com', hash_password('password123'), 'Jane Smith', '+1234567891', 'janesmith', true, true),
('550e8400-e29b-41d4-a716-446655440002', 'mike.johnson@example.com', hash_password('password123'), 'Mike Johnson', '+1234567892', 'mikejohnson', true, false)
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- SAMPLE PROFILES
-- =====================================================

-- Insert sample profiles
INSERT INTO profiles (id, email, name, phone, username, default_experience, default_skills, default_education, default_projects) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'john.doe@example.com', 'John Doe', '+1234567890', 'johndoe', 
 'Software Engineer with 5 years of experience in full-stack development', 
 'Python, JavaScript, React, Node.js, PostgreSQL, AWS', 
 'Bachelor of Science in Computer Science, University of Technology', 
 'E-commerce platform, Mobile app development, API integration'),
 
('550e8400-e29b-41d4-a716-446655440001', 'jane.smith@example.com', 'Jane Smith', '+1234567891', 'janesmith', 
 'Data Scientist with expertise in machine learning and analytics', 
 'Python, R, SQL, TensorFlow, Pandas, Scikit-learn, Tableau', 
 'Master of Science in Data Science, Data University', 
 'Predictive modeling project, Customer segmentation analysis, Real-time analytics dashboard'),
 
('550e8400-e29b-41d4-a716-446655440002', 'mike.johnson@example.com', 'Mike Johnson', '+1234567892', 'mikejohnson', 
 'DevOps Engineer with experience in cloud infrastructure and automation', 
 'Docker, Kubernetes, AWS, Terraform, Jenkins, Linux, Bash', 
 'Bachelor of Engineering in Computer Engineering, Tech Institute', 
 'CI/CD pipeline setup, Infrastructure as Code, Monitoring system implementation')
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- SAMPLE DOCUMENTS
-- =====================================================

-- Insert sample documents
INSERT INTO documents (user_id, doc_type, title, content_json, content_text) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'resume', 'John Doe - Software Engineer Resume', 
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1234567890", "summary": "Experienced software engineer with 5 years in full-stack development", "experience": [{"title": "Senior Software Engineer", "company": "Tech Corp", "dates": "2020-2024", "bullets": ["Led development of microservices architecture", "Improved system performance by 40%"]}], "skills": ["Python", "JavaScript", "React", "Node.js"]}', 
 'John Doe - Software Engineer with 5 years of experience...'),

('550e8400-e29b-41d4-a716-446655440000', 'cover_letter', 'Cover Letter - Tech Corp - Software Engineer', 
 NULL, 
 'Dear Hiring Manager, I am writing to express my interest in the Software Engineer position at Tech Corp...'),

('550e8400-e29b-41d4-a716-446655440001', 'resume', 'Jane Smith - Data Scientist Resume', 
 '{"name": "Jane Smith", "email": "jane.smith@example.com", "phone": "+1234567891", "summary": "Data Scientist with expertise in machine learning and analytics", "experience": [{"title": "Senior Data Scientist", "company": "Data Corp", "dates": "2019-2024", "bullets": ["Developed ML models with 95% accuracy", "Led data analytics team of 5"]}], "skills": ["Python", "R", "SQL", "TensorFlow"]}', 
 'Jane Smith - Data Scientist with expertise in machine learning...'),

('550e8400-e29b-41d4-a716-446655440002', 'resume', 'Mike Johnson - DevOps Engineer Resume', 
 '{"name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1234567892", "summary": "DevOps Engineer with experience in cloud infrastructure", "experience": [{"title": "DevOps Engineer", "company": "Cloud Corp", "dates": "2021-2024", "bullets": ["Implemented CI/CD pipelines", "Reduced deployment time by 60%"]}], "skills": ["Docker", "Kubernetes", "AWS", "Terraform"]}', 
 'Mike Johnson - DevOps Engineer with experience in cloud infrastructure...')
ON CONFLICT DO NOTHING;

-- =====================================================
-- SAMPLE JOB APPLICATIONS
-- =====================================================

-- Insert sample job applications
INSERT INTO job_applications (user_id, company, position, status, application_date, deadline, notes, job_description, salary_range, location, job_url) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'Tech Corp', 'Senior Software Engineer', 'applied', '2024-01-15', '2024-02-15', 'Applied through company website', 'Looking for experienced software engineer to join our team', '$80,000 - $120,000', 'San Francisco, CA', 'https://techcorp.com/careers/senior-software-engineer'),

('550e8400-e29b-41d4-a716-446655440000', 'StartupXYZ', 'Full Stack Developer', 'interview', '2024-01-10', '2024-02-10', 'Phone interview scheduled for next week', 'Full-stack developer position at growing startup', '$70,000 - $100,000', 'Remote', 'https://startupxyz.com/jobs/full-stack-developer'),

('550e8400-e29b-41d4-a716-446655440001', 'Data Corp', 'Senior Data Scientist', 'applied', '2024-01-20', '2024-02-20', 'Applied via LinkedIn', 'Senior data scientist role focusing on ML and analytics', '$90,000 - $130,000', 'New York, NY', 'https://datacorp.com/careers/senior-data-scientist'),

('550e8400-e29b-41d4-a716-446655440001', 'Analytics Inc', 'Machine Learning Engineer', 'offer', '2024-01-05', '2024-02-05', 'Received offer, considering', 'ML engineer position with focus on deep learning', '$85,000 - $125,000', 'Seattle, WA', 'https://analyticsinc.com/jobs/ml-engineer'),

('550e8400-e29b-41d4-a716-446655440002', 'Cloud Corp', 'Senior DevOps Engineer', 'applied', '2024-01-18', '2024-02-18', 'Applied through referral', 'Senior DevOps engineer for cloud infrastructure', '$95,000 - $140,000', 'Austin, TX', 'https://cloudcorp.com/careers/senior-devops-engineer'),

('550e8400-e29b-41d4-a716-446655440002', 'InfraTech', 'DevOps Engineer', 'rejected', '2024-01-12', '2024-02-12', 'Position filled internally', 'DevOps engineer for infrastructure automation', '$80,000 - $110,000', 'Denver, CO', 'https://infratech.com/jobs/devops-engineer')
ON CONFLICT DO NOTHING;

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'Sample data inserted successfully!' as status;

-- Show sample data counts
SELECT 'Sample data counts:' as info;
SELECT 
    'Users' as table_name, 
    COUNT(*) as record_count 
FROM users
UNION ALL
SELECT 
    'Profiles' as table_name, 
    COUNT(*) as record_count 
FROM profiles
UNION ALL
SELECT 
    'Documents' as table_name, 
    COUNT(*) as record_count 
FROM documents
UNION ALL
SELECT 
    'Job Applications' as table_name, 
    COUNT(*) as record_count 
FROM job_applications;

-- Show sample users
SELECT 'Sample users:' as info;
SELECT id, email, name, username, is_active, email_verified FROM users LIMIT 5;

-- Show sample job applications by status
SELECT 'Job applications by status:' as info;
SELECT status, COUNT(*) as count FROM job_applications GROUP BY status ORDER BY count DESC;
