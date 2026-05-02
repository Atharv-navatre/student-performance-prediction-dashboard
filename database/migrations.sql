-- =============================================
-- Student Performance Prediction Dashboard
-- Supabase schema migration
-- =============================================

-- TABLE 1: students
DROP TABLE IF EXISTS students CASCADE;

CREATE TABLE students (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_code TEXT UNIQUE NOT NULL,
    attendance_pct FLOAT,
    study_hours_per_day FLOAT,
    previous_score FLOAT,
    motivation_level INTEGER,
    tutoring_sessions INTEGER,
    sleep_hours FLOAT,
    extracurricular_activities INTEGER,
    internet_access INTEGER,
    family_income_level INTEGER,
    parental_education_level INTEGER,
    teacher_quality INTEGER,
    distance_from_home INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- TABLE 2: predictions
DROP TABLE IF EXISTS predictions CASCADE;

CREATE TABLE predictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid REFERENCES students(id) ON DELETE CASCADE,
    predicted_score FLOAT NOT NULL,
    performance_category TEXT NOT NULL,
    is_at_risk BOOLEAN NOT NULL DEFAULT false,
    model_used TEXT,
    model_version TEXT,
    predicted_at TIMESTAMPTZ DEFAULT now()
);

-- TABLE 3: performance_history
DROP TABLE IF EXISTS performance_history CASCADE;

CREATE TABLE performance_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid REFERENCES students(id) ON DELETE CASCADE,
    period TEXT NOT NULL,
    predicted_score FLOAT,
    performance_category TEXT,
    recorded_at TIMESTAMPTZ DEFAULT now()
);

-- TABLE 4: insights_log
DROP TABLE IF EXISTS insights_log CASCADE;

CREATE TABLE insights_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    total_students INTEGER,
    at_risk_count INTEGER,
    at_risk_pct FLOAT,
    avg_score FLOAT,
    category_distribution JSONB,
    top_risk_factors JSONB,
    recommendations JSONB,
    generated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_predictions_student_id
    ON predictions(student_id);

CREATE INDEX IF NOT EXISTS idx_predictions_is_at_risk
    ON predictions(is_at_risk);

CREATE INDEX IF NOT EXISTS idx_predictions_category
    ON predictions(performance_category);

CREATE INDEX IF NOT EXISTS idx_history_student_id
    ON performance_history(student_id);

CREATE INDEX IF NOT EXISTS idx_students_code
    ON students(student_code);

-- =============================================
-- Migration complete
-- Tables: students, predictions,
--         performance_history, insights_log
-- Run this in: Supabase Dashboard > SQL Editor
-- =============================================
