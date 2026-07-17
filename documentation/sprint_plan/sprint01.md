# Sprint 01 — Infrastructure & Database Setup

> **Project:** SkillBridge — Multi-Agent Adaptive Learning System
> **Sprint:** 1 of 10
> **Estimated Duration:** ~3 hours
> **Critical Path:** ✅ YES — nothing else can start without this
> **Status:** 🔲 Not started

---

## Goal

Supabase project live, schema applied, pgvector working, `job_skills` seeded with embeddings, all secrets configured in `.env`, and core shared modules (`config.py`, `db/client.py`, `llm_client.py`, `state.py`) written.

---

## Success Criteria

| # | Check | How to verify |
|---|-------|---------------|
| SC-1 | `SELECT COUNT(*) FROM job_skills` returns ≥ 100 rows | Supabase SQL editor |
| SC-2 | All 6 tables exist with correct columns | `\dt` in Supabase SQL editor |
| SC-3 | pgvector extension active | `SELECT extname FROM pg_extension WHERE extname = 'vector'` returns 1 row |
| SC-4 | `IVFFlat` index on `job_skills.embedding` exists | `\di` in Supabase SQL editor |
| SC-5 | `Settings()` loads without error when `.env` present | Unit test `test_settings_loads_from_env` passes |
| SC-6 | `get_supabase().table('profiles').select('id').limit(1).execute()` returns no error | Integration test `test_supabase_ping` passes |
| SC-7 | `match_job_skills` SQL function exists and returns results | Integration test `test_job_skills_populated` passes |

---

## Pre-Sprint Checklist

Before writing a single line of code, confirm the following:

- [ ] Supabase project created (free tier) — note the project URL + service role key
- [ ] DeepSeek API key active and usable from India
- [ ] Gemini API key active (for `gemini-embedding-001`)
- [ ] Resend API key active (free tier)
- [ ] LangSmith API key ready (free tier)
- [ ] `build/` directory exists in project root (create if not)
- [ ] `job_skills_dataset.csv` curated — 100–200 rows of `role, skill, importance_level` covering 5–10 target roles

> [!IMPORTANT]
> The `job_skills_dataset.csv` MUST be hand-curated before `embed_job_skills.py` can run. Plan 20–30 minutes to create or source this CSV. Target roles: backend dev, frontend dev, data analyst, ML engineer, DevOps engineer, product manager, UI/UX designer, full-stack dev, QA engineer, cloud engineer.

---

## Build Target Layout

All code goes inside `build/`. After Sprint 1, the following paths must exist:

```
build/
└── backend/
    ├── src/
    │   ├── core/
    │   │   ├── config.py           # Settings (pydantic-settings)
    │   │   └── llm_client.py       # get_llm() factory
    │   ├── db/
    │   │   ├── schema.sql          # Full 6-table schema + RLS + IVFFlat
    │   │   └── client.py           # get_supabase() factory
    │   └── agents/
    │       └── state.py            # SkillBridgeState TypedDict
    ├── scripts/
    │   ├── job_skills_dataset.csv  # Manually curated seed data
    │   └── embed_job_skills.py     # One-time embedding + insert script
    ├── tests/
    │   ├── unit/
    │   │   └── test_config.py
    │   └── integration/
    │       └── test_db_connection.py
    ├── .env.example                # All secret names, NO values
    ├── .env                        # Real secrets — gitignored
    └── pyproject.toml              # uv-managed dependencies
```

---

## Tasks

### Task 1 — Scaffold `build/` and Python project

**File:** `build/backend/pyproject.toml`
**Time estimate:** 15 min

1. Create `build/backend/` directory structure as shown above.
2. Initialize with `uv`:
   ```bash
   cd build/backend
   uv init --name skillbridge-backend --python 3.11
   ```
3. Add dependencies to `pyproject.toml`:
   ```toml
   [project]
   name = "skillbridge-backend"
   version = "0.1.0"
   requires-python = ">=3.11"
   dependencies = [
     "fastapi>=0.115",
     "uvicorn>=0.30",
     "pydantic>=2.7",
     "pydantic-settings>=2.3",
     "langchain>=0.3",
     "langchain-deepseek>=0.1",
     "langgraph>=0.2",
     "supabase>=2.5",
     "google-generativeai>=0.8",
     "resend>=2.0",
     "tenacity>=8.3",
     "modal>=0.64",
     "python-dotenv>=1.0",
   ]

   [tool.pytest.ini_options]
   testpaths = ["tests", "evals"]
   ```
4. Run `uv pip install -r pyproject.toml` to verify all packages resolve.

**Verify:** `uv pip list` shows all packages with no conflict errors.

---

### Task 2 — Write `src/core/config.py`

**File:** `build/backend/src/core/config.py`
**Time estimate:** 10 min

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    deepseek_api_key: str
    gemini_api_key: str
    supabase_url: str
    supabase_service_key: str
    resend_api_key: str
    langsmith_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
```

**Verify:** `python -c "from src.core.config import settings; print(settings.supabase_url)"` prints the URL without error.

---

### Task 3 — Write `.env.example` and `.env`

**Files:** `build/backend/.env.example`, `build/backend/.env`
**Time estimate:** 5 min

`.env.example` (commit this):
```
DEEPSEEK_API_KEY=
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
RESEND_API_KEY=
LANGSMITH_API_KEY=
```

`.env` (never commit — fill in real values):
```
DEEPSEEK_API_KEY=sk-...
GEMINI_API_KEY=AI...
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
RESEND_API_KEY=re_...
LANGSMITH_API_KEY=ls__...
```

Also add `.env` to `build/backend/.gitignore`.

---

### Task 4 — Apply `schema.sql` in Supabase

**File:** `build/backend/src/db/schema.sql`
**Time estimate:** 30 min

Apply in the **Supabase SQL editor**, strictly in this order:

#### Step 4a — Enable pgvector
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### Step 4b — `profiles` table
```sql
CREATE TABLE IF NOT EXISTS profiles (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email          TEXT UNIQUE NOT NULL,
    name           TEXT,
    goal           TEXT,
    hours_per_week INT DEFAULT 10,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "profiles_self" ON profiles
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);
```

#### Step 4c — `skill_gaps` table
```sql
CREATE TABLE IF NOT EXISTS skill_gaps (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                  UUID REFERENCES profiles(id) ON DELETE CASCADE,
    skill_gap_report         JSONB NOT NULL,
    overall_readiness_percent INT,
    created_at               TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;
CREATE POLICY "skill_gaps_self" ON skill_gaps
    USING (auth.uid() = user_id);
```

#### Step 4d — `learning_plans` table
```sql
CREATE TABLE IF NOT EXISTS learning_plans (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID REFERENCES profiles(id) ON DELETE CASCADE,
    milestones              JSONB NOT NULL,
    current_milestone_index INT DEFAULT 0,
    plan_revision_count     INT DEFAULT 0,
    is_active               BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Partial unique index: only one active plan per user at a time
CREATE UNIQUE INDEX IF NOT EXISTS one_active_plan_per_user
    ON learning_plans(user_id)
    WHERE is_active = TRUE;

ALTER TABLE learning_plans ENABLE ROW LEVEL SECURITY;
CREATE POLICY "learning_plans_self" ON learning_plans
    USING (auth.uid() = user_id);
```

#### Step 4e — `quiz_results` table
```sql
CREATE TABLE IF NOT EXISTS quiz_results (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID REFERENCES profiles(id) ON DELETE CASCADE,
    quiz_id        TEXT UNIQUE NOT NULL,
    date           DATE NOT NULL DEFAULT CURRENT_DATE,
    questions      JSONB,
    answers        JSONB,
    score          FLOAT,
    recommendation TEXT,
    sent_at        TIMESTAMPTZ,
    submitted_at   TIMESTAMPTZ,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "quiz_results_self" ON quiz_results
    USING (auth.uid() = user_id);
```

#### Step 4f — `job_skills` table
```sql
CREATE TABLE IF NOT EXISTS job_skills (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role             TEXT NOT NULL,
    skill            TEXT NOT NULL,
    importance_level INT NOT NULL CHECK (importance_level BETWEEN 1 AND 5),
    embedding        vector(768)
);

-- IVFFlat index — run AFTER embed_job_skills.py has seeded >= 100 rows
-- CREATE INDEX IF NOT EXISTS job_skills_embedding_idx
--     ON job_skills USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 10);
```

> [!NOTE]
> The IVFFlat `CREATE INDEX` is **commented out**. Run it after `embed_job_skills.py` has seeded ≥ 100 rows — pgvector requires existing data to build an IVFFlat index correctly.

#### Step 4g — `weekly_reports` table
```sql
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
```

#### Step 4h — `match_job_skills` RAG function
```sql
CREATE OR REPLACE FUNCTION match_job_skills(
    query_embedding vector(768),
    match_count     INT DEFAULT 20
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
```

**Verify:** Run each statement in Supabase SQL editor. Check Table Editor — all 6 tables must appear.

---

### Task 5 — Write `src/db/client.py`

**File:** `build/backend/src/db/client.py`
**Time estimate:** 5 min

```python
from supabase import create_client, Client
from src.core.config import settings


def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)
```

**Verify:** `python -c "from src.db.client import get_supabase; c = get_supabase(); print('OK')"` prints `OK`.

---

### Task 6 — Write `src/core/llm_client.py`

**File:** `build/backend/src/core/llm_client.py`
**Time estimate:** 10 min

```python
from langchain_deepseek import ChatDeepSeek
from src.core.config import settings


def get_llm(temperature: float = 0.2) -> ChatDeepSeek:
    return ChatDeepSeek(
        model="deepseek-chat",
        temperature=temperature,
        api_key=settings.deepseek_api_key,
    )
```

**Verify:** `python -c "from src.core.llm_client import get_llm; print('OK')"` prints `OK`.

---

### Task 7 — Write `src/agents/state.py`

**File:** `build/backend/src/agents/state.py`
**Time estimate:** 10 min

```python
from typing import TypedDict


class SkillBridgeState(TypedDict, total=False):
    # User context
    user_id: str
    user_email: str
    user_goal: str
    current_skills: list[str]
    hours_per_week: int

    # Agent 1 output
    skill_gap_report: dict          # Matches SkillGapReport schema

    # Agent 2 output
    learning_plan: list[dict]       # list[Milestone]
    current_milestone_index: int
    plan_revision_count: int

    # Agent 3a / 3b working state
    morning_brief: dict             # Matches MorningBrief schema
    quiz_questions: list[dict]      # list[QuizQuestion]
    quiz_id: str
    quiz_answers: list[int]         # Student's selected option indices
    quiz_result: dict               # Matches QuizResult schema

    # Agent 4 output
    weekly_report: dict             # Matches WeeklyReport schema

    # Shared
    progress_log: list[str]         # Audit trail of agent actions
```

**Verify:** `python -c "from src.agents.state import SkillBridgeState; print('OK')"` prints `OK`.

---

### Task 8 — Curate `job_skills_dataset.csv`

**File:** `build/backend/scripts/job_skills_dataset.csv`
**Time estimate:** 20 min

CSV columns: `role, skill, importance_level` (1 = nice-to-have → 5 = must-have). Minimum 100 rows.

| Role | Target skill count |
|------|--------------------|
| Backend Developer | 15 |
| Frontend Developer | 15 |
| Data Analyst | 12 |
| ML Engineer | 15 |
| DevOps Engineer | 12 |
| Full Stack Developer | 12 |
| UI/UX Designer | 10 |
| Cloud Engineer | 12 |
| QA Engineer | 10 |
| Product Manager | 10 |

Sample rows:
```csv
role,skill,importance_level
Backend Developer,Python,5
Backend Developer,FastAPI,4
Backend Developer,PostgreSQL,4
Backend Developer,REST APIs,5
Backend Developer,Docker,4
Frontend Developer,JavaScript,5
Frontend Developer,React,4
...
```

**Verify:** Row count ≥ 101 (100 data rows + 1 header).

---

### Task 9 — Write and run `embed_job_skills.py`

**File:** `build/backend/scripts/embed_job_skills.py`
**Time estimate:** 20 min write + 10 min run

```python
"""One-time script: reads job_skills_dataset.csv, embeds each row, inserts into Supabase."""
import csv
import time
import sys
import google.generativeai as genai
from src.core.config import settings
from src.db.client import get_supabase

genai.configure(api_key=settings.gemini_api_key)
supabase = get_supabase()

BATCH_SIZE = 20  # Stay within Gemini free-tier rate limits


def embed_text(text: str) -> list[float]:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def main():
    csv_path = "scripts/job_skills_dataset.csv"
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"Loaded {len(rows)} rows from {csv_path}")

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        records = []
        for row in batch:
            text = f"{row['role']}: {row['skill']}"
            embedding = embed_text(text)
            records.append({
                "role": row["role"],
                "skill": row["skill"],
                "importance_level": int(row["importance_level"]),
                "embedding": embedding,
            })

        supabase.table("job_skills").insert(records).execute()
        print(f"  Inserted batch {i // BATCH_SIZE + 1} ({len(records)} rows)")
        time.sleep(1)  # Rate limit buffer

    print("\nDone! Now run the IVFFlat CREATE INDEX in Supabase SQL editor:")
    print("  CREATE INDEX IF NOT EXISTS job_skills_embedding_idx")
    print("      ON job_skills USING ivfflat (embedding vector_cosine_ops)")
    print("      WITH (lists = 10);")


if __name__ == "__main__":
    main()
```

**After running**, build the IVFFlat index in Supabase SQL editor:
```sql
CREATE INDEX IF NOT EXISTS job_skills_embedding_idx
    ON job_skills USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);
```

**Run command:**
```bash
cd build/backend
python scripts/embed_job_skills.py
```

**Verify:** `SELECT COUNT(*) FROM job_skills;` in Supabase SQL editor returns ≥ 100.

---

### Task 10 — Write unit tests

**File:** `build/backend/tests/unit/test_config.py`
**Time estimate:** 10 min

```python
import pytest
from pydantic import ValidationError


def test_settings_loads_from_env(monkeypatch):
    """Settings instantiates successfully when all required env vars are present."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key")
    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")

    from src.core.config import Settings
    s = Settings()
    assert s.supabase_url == "https://test.supabase.co"


def test_settings_missing_key_raises(monkeypatch):
    """Settings raises when a required env var is missing."""
    for key in ["DEEPSEEK_API_KEY", "GEMINI_API_KEY", "SUPABASE_URL",
                "SUPABASE_SERVICE_KEY", "RESEND_API_KEY", "LANGSMITH_API_KEY"]:
        monkeypatch.delenv(key, raising=False)

    from src.core.config import Settings
    with pytest.raises((ValidationError, Exception)):
        Settings()
```

---

### Task 11 — Write integration tests

**File:** `build/backend/tests/integration/test_db_connection.py`
**Time estimate:** 10 min

```python
"""Integration tests — require real Supabase credentials in .env"""
import pytest
from src.db.client import get_supabase


@pytest.fixture(scope="module")
def supabase():
    return get_supabase()


def test_supabase_ping(supabase):
    """Can connect to Supabase and query profiles table without error."""
    result = supabase.table("profiles").select("id").limit(1).execute()
    assert result is not None


def test_job_skills_populated(supabase):
    """job_skills table has at least 100 rows after seeding."""
    result = supabase.table("job_skills").select("id", count="exact").execute()
    assert result.count >= 100


def test_all_six_tables_exist(supabase):
    """All 6 required tables are present and queryable."""
    tables = [
        "profiles", "skill_gaps", "learning_plans",
        "quiz_results", "job_skills", "weekly_reports",
    ]
    for table in tables:
        result = supabase.table(table).select("*").limit(0).execute()
        assert result is not None, f"Table '{table}' unreachable"


def test_match_job_skills_function_callable(supabase):
    """match_job_skills RPC function exists and returns a list."""
    dummy_vector = [0.0] * 768
    result = supabase.rpc(
        "match_job_skills",
        {"query_embedding": dummy_vector, "match_count": 5}
    ).execute()
    assert isinstance(result.data, list)
```

---

## Execution Order

```
Step 1   Create build/backend/ directory structure
Step 2   Task 1  — scaffold pyproject.toml + install deps (uv)
Step 3   Task 2  — write config.py
Step 4   Task 3  — write .env.example + .env (fill secrets)
Step 5   Task 7  — write agents/state.py
Step 6   Task 5  — write db/client.py
Step 7   Task 6  — write core/llm_client.py
Step 8   Task 4  — apply schema.sql in Supabase (steps 4a → 4h)
Step 9   Task 8  — curate job_skills_dataset.csv
Step 10  Task 9  — run embed_job_skills.py + build IVFFlat index
Step 11  Task 10 — write + run unit tests
Step 12  Task 11 — write + run integration tests
Step 13  Verify all 7 success criteria
```

---

## Tests Summary

| File | Type | Count | Requires secrets |
|------|------|-------|-----------------|
| `tests/unit/test_config.py` | Unit | 2 | No |
| `tests/integration/test_db_connection.py` | Integration | 4 | Yes (Supabase) |

```bash
# Unit tests (no secrets needed)
cd build/backend && pytest tests/unit/test_config.py -v

# Integration tests (requires .env)
cd build/backend && pytest tests/integration/test_db_connection.py -v
```

---

## Sprint 1 Exit Gate

> [!IMPORTANT]
> Do **not** start Sprint 2 until ALL of the following pass:
>
> - [ ] `pytest tests/unit/test_config.py -v` → **2 passed**
> - [ ] `pytest tests/integration/test_db_connection.py -v` → **4 passed**
> - [ ] `SELECT COUNT(*) FROM job_skills` → **≥ 100**
> - [ ] `SELECT extname FROM pg_extension WHERE extname = 'vector'` → **1 row**
> - [ ] IVFFlat index created on `job_skills.embedding`
> - [ ] All 6 tables visible in Supabase Table Editor
> - [ ] `match_job_skills` RPC callable without error

---

*Sprint 01 plan created: 2026-07-17*
*Derived from: `documentation/plan/implementation_plan.md` — Sprint 1 section*
*Project: SkillBridge — AICTE AI Automation & Intelligent Solutions, IBM SkillsBuild 2026*
