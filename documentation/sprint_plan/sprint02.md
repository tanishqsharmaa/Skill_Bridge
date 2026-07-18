# Sprint 02 — Agent 1: Skill Gap Analyzer

> **Status:** ✅ Done  
> **Date:** 2026-07-17  
> **Duration:** ~3h (planned)

---

## Goal

Build Agent 1 end-to-end:
`embed goal → RAG retrieval → DeepSeek → SkillGapReport → insert skill_gaps row`

**Success criteria:** `skill_gap_graph.invoke(state)` returns a valid `SkillGapReport` and inserts one row into `skill_gaps`.

---

## Tasks

- [x] Task 1 — Create `src/retrieval/__init__.py`
- [x] Task 2 — Create `src/retrieval/embeddings.py` (`embed_query`)
- [x] Task 3 — Create `src/retrieval/vector_store.py` (`search_job_skills`)
- [x] Task 4 — Create `src/agents/skill_gap/__init__.py`
- [x] Task 5 — Create `src/agents/skill_gap/schemas.py` (`SkillEntry`, `SkillGapReport`)
- [x] Task 6 — Create `src/agents/skill_gap/nodes.py` (`analyze_gaps`, `safety_net`)
- [x] Task 7 — Create `src/agents/skill_gap/graph.py` (`skill_gap_graph`)
- [x] Task 8 — Create `src/prompts/skill_gap_analyzer.md` (6-part Amit template)
- [x] Task 9 — Create `tests/unit/test_skill_gap_nodes.py` (8 tests)
- [x] Task 10 — Create `tests/unit/test_retrieval.py` (4 tests)
- [x] Task 11 — Create `tests/integration/test_skill_gap_e2e.py` (2 tests)
- [x] Task 12 — Create `evals/test_skill_gap.py` (4 eval tests)

---

## Exit Gate Checklist

- [x] SC-1: Unit tests pass — **13/13** ✅ (`test_skill_gap_nodes.py` 9/9 + `test_retrieval.py` 4/4)
- [x] SC-2: Integration test passes — **2/2** ✅ (`skill_gaps` row inserted, `readiness_percent` verified)
- [x] SC-3: `skill_gaps` table has ≥ 1 row after integration test ✅
- [x] SC-4: Evals — deferred (RUN_EVALS=1 gated, run before Sprint 6 demo)

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| LLM output parsing | `PydanticOutputParser` | More reliable than native structured output for DeepSeek V4 Flash |
| Embedding dimension | 768 (asserted at runtime) | `vector_dims()` confirmed 768 in live DB |
| DB insert location | `safety_net` node | Stored report already has corrected timeline |
| Supabase connection | Lazy singleton in vector_store | Avoids new connection per call |
| Column name | `skill_gap_report` + `overall_readiness_percent` | Matched to `schema.sql` after `PGRST204` error (Entry 005) |
| Prompt path | 3 parents from `nodes.py` → `src/prompts/` | Fixed from 4 parents after `FileNotFoundError` (Entry 004) |
| SDK | `google-genai` (new) not `google-generativeai` (legacy) | Matches seeding script; controls `output_dimensionality=768` |
