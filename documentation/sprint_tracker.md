# SkillBridge — Sprint Tracker

> **Project:** SkillBridge — Multi-Agent Adaptive Learning System
> **Deadline:** 20 July 2026
> **Stack:** SvelteKit · FastAPI · Modal · LangGraph · Supabase · DeepSeek V4 Flash · Resend

---

## Overall Progress

| Sprint | Name | Status | Duration | Notes |
|--------|------|--------|----------|-------|
| 1 | Infrastructure & Database Setup | ✅ Done | ~3h | Critical path |
| 2 | Agent 1 — Skill Gap Analyzer | ✅ Done | ~3h | Critical path |
| 3 | Agent 2 — Learning Path Planner | 🔲 Not started | ~2h | Critical path |
| 4 | Agent 3a — Morning Brief | 🔲 Not started | ~2h | Critical path |
| 5 | Agent 3b — Quiz Conductor + Evaluator | 🔲 Not started | ~4h | Critical path |
| 6 | FastAPI + Modal Deployment | 🔲 Not started | ~2h | Critical path |
| 7 | SvelteKit Frontend | 🔲 Not started | ~4h | Critical path |
| 8 | Agent 4 + Supabase Auth | 🔲 Not started | ~3h | High priority |
| 9 | LangSmith Tracing + Polish | 🔲 Not started | ~2h | High priority |
| 10 | Evidence, PPT, Submission | 🔲 Not started | ~3h | High priority |

**Status legend:** 🔲 Not started · 🔄 In progress · ✅ Done · 🚧 Blocked

---

## Sprint 1 Detail

**Status:** ✅ Done
**Started:** 2026-07-17
**Completed:** 2026-07-17

### Tasks
- [x] Task 1 — Scaffold `build/backend/` + `pyproject.toml`
- [x] Task 2 — Write `src/core/config.py`
- [x] Task 3 — Write `.env.example` + `.gitignore`
- [x] Task 4 — Apply `schema.sql` in Supabase (6 tables + RLS + pgvector + IVFFlat + match_job_skills fn) ✅
- [x] Task 5 — Write `src/db/client.py`
- [x] Task 6 — Write `src/core/llm_client.py`
- [x] Task 7 — Write `src/agents/state.py`
- [x] Task 8 — Curate `scripts/job_skills_dataset.csv` (122 rows ✅)
- [x] Task 9 — Run `scripts/embed_job_skills.py` (121/122 rows ✅) + IVFFlat index built ✅
- [x] Task 10 — Write + run unit tests (`test_config.py` — 2/2 ✅)
- [x] Task 11 — Run integration tests (`test_db_connection.py` — 4/4 ✅)

### Exit Gate Checklist
- [x] SC-1: `SELECT COUNT(*) FROM job_skills` ≥ 100 — **121 rows** ✅
- [x] SC-2: All 6 tables exist ✅
- [x] SC-3: pgvector extension active ✅
- [x] SC-4: IVFFlat index on `job_skills.embedding` ✅
- [x] SC-5: Unit tests pass — **2/2** ✅
- [x] SC-6: Integration tests pass — **4/4** ✅
- [x] SC-7: `match_job_skills` RPC callable ✅

---

## Sprint 2 Detail

**Status:** ✅ Done  
**Started:** 2026-07-17  
**Completed:** 2026-07-17

### Tasks
- [x] Task 1 — Create `src/retrieval/` package (`embeddings.py`, `vector_store.py`)
- [x] Task 2 — Create `src/agents/skill_gap/` package (`schemas.py`, `nodes.py`, `graph.py`)
- [x] Task 3 — Create `src/prompts/skill_gap_analyzer.md`
- [x] Task 4 — Write unit tests: `test_skill_gap_nodes.py` (8 tests) + `test_retrieval.py` (4 tests)
- [x] Task 5 — Write integration test: `test_skill_gap_e2e.py` (2 tests)
- [x] Task 6 — Write evals: `evals/test_skill_gap.py` (4 tests, RUN_EVALS=1 gated)

### Exit Gate Checklist
- [x] SC-1: Unit tests pass — **13/13** ✅
- [x] SC-2: Integration test passes — `skill_gaps` row inserted ✅
- [x] SC-3: Evals pass — deferred (RUN_EVALS=1 gated, run before Sprint 6)

---

*Last updated: 2026-07-18 — Sprint 2 closed ✅ | Sprint 3 (Agent 2 — Learning Path Planner) next*
