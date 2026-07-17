-- ============================================================
-- SkillBridge — Supabase Schema
-- Apply each block in the Supabase SQL editor IN ORDER.
-- ============================================================

-- ── 0. Extensions ────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;


-- ── 1. profiles ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email          TEXT UNIQUE NOT NULL,
    name           TEXT,
    goal           TEXT,
    hours_per_week INT DEFAULT 10,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_self_select" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "profiles_self_insert" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "profiles_self_update" ON profiles
    FOR UPDATE USING (auth.uid() = id);


-- ── 2. skill_gaps ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS skill_gaps (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                   UUID REFERENCES profiles(id) ON DELETE CASCADE,
    skill_gap_report          JSONB NOT NULL,
    overall_readiness_percent INT,
    created_at                TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "skill_gaps_self" ON skill_gaps
    USING (auth.uid() = user_id);


-- ── 3. learning_plans ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS learning_plans (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID REFERENCES profiles(id) ON DELETE CASCADE,
    milestones              JSONB NOT NULL,
    current_milestone_index INT DEFAULT 0,
    plan_revision_count     INT DEFAULT 0,
    is_active               BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Only one active plan per user at a time (enforced by partial unique index)
CREATE UNIQUE INDEX IF NOT EXISTS one_active_plan_per_user
    ON learning_plans(user_id)
    WHERE is_active = TRUE;

ALTER TABLE learning_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "learning_plans_self" ON learning_plans
    USING (auth.uid() = user_id);


-- ── 4. quiz_results ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quiz_results (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID REFERENCES profiles(id) ON DELETE CASCADE,
    quiz_id        TEXT UNIQUE NOT NULL,   -- {user_id_prefix}_{date}_{slug}
    date           DATE NOT NULL DEFAULT CURRENT_DATE,
    questions      JSONB,                  -- list[QuizQuestion] at generation time
    answers        JSONB,                  -- student's submitted answers
    score          FLOAT,                  -- 0.0–100.0
    recommendation TEXT,                   -- 'advance' | 'review'
    sent_at        TIMESTAMPTZ,            -- when quiz link email was sent
    submitted_at   TIMESTAMPTZ,            -- when student submitted answers
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "quiz_results_self" ON quiz_results
    USING (auth.uid() = user_id);


-- ── 5. job_skills ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_skills (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role             TEXT NOT NULL,
    skill            TEXT NOT NULL,
    importance_level INT  NOT NULL CHECK (importance_level BETWEEN 1 AND 5),
    embedding        vector(768)   -- gemini-embedding-001 output dimension
);

-- NOTE: Run the IVFFlat index AFTER embed_job_skills.py has seeded >= 100 rows.
-- Uncomment and run this block after seeding:
--
-- CREATE INDEX IF NOT EXISTS job_skills_embedding_idx
--     ON job_skills USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 10);


-- ── 6. weekly_reports ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS weekly_reports (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID REFERENCES profiles(id) ON DELETE CASCADE,
    week_start           DATE NOT NULL,
    milestones_completed INT,
    avg_quiz_score       FLOAT,
    linkedin_post_text   TEXT,
    report_html          TEXT,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, week_start)
);

ALTER TABLE weekly_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "weekly_reports_self" ON weekly_reports
    USING (auth.uid() = user_id);


-- ── 7. match_job_skills — RAG retrieval function ──────────────
-- Called by Agent 1 to perform cosine similarity search over job_skills.
CREATE OR REPLACE FUNCTION match_job_skills(
    query_embedding  vector(768),
    match_count      INT DEFAULT 20
)
RETURNS TABLE (
    id               UUID,
    role             TEXT,
    skill            TEXT,
    importance_level INT,
    similarity       FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        role,
        skill,
        importance_level,
        1 - (embedding <=> query_embedding) AS similarity
    FROM job_skills
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;


-- ── Verification queries (run after applying all blocks) ──────
-- SELECT COUNT(*) FROM profiles;           -- should exist (0 rows OK)
-- SELECT COUNT(*) FROM skill_gaps;         -- should exist (0 rows OK)
-- SELECT COUNT(*) FROM learning_plans;     -- should exist (0 rows OK)
-- SELECT COUNT(*) FROM quiz_results;       -- should exist (0 rows OK)
-- SELECT COUNT(*) FROM job_skills;         -- should be >= 100 after seeding
-- SELECT COUNT(*) FROM weekly_reports;     -- should exist (0 rows OK)
-- SELECT extname FROM pg_extension WHERE extname = 'vector';  -- should return 1 row
