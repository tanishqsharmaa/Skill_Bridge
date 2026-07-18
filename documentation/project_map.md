# SkillBridge — Live Project Map

> **Purpose:** Tracks the *actual* file/folder state of the repository as it is built.
> Update every time a file or folder is added, deleted, or renamed.
> Do NOT confuse with `project_structure.md` (the original plan).

*Last updated: 2026-07-18 — Sprint 2 closed ✅ | Sprint 3 next*

---

## Repository Root

```
F:\IBM_internship\sunmission\Project\
├── AGENTS.md                              # Behavioral guidelines (updated: section 8 — frequent commits)
├── Build/                                 # All code lives here
├── Planning/                              # Alias / symlink directory (mirrors documentation/)
└── documentation/
    ├── plan/
    │   └── implementation_plan.md         # Master 10-sprint roadmap
    ├── sprint_plan/
    │   ├── sprint01.md                    # Sprint 1 detailed task plan ✅
    │   └── sprint02.md                    # Sprint 2 detailed task plan ✅
    ├── error_log.md                       # Bug log — 5 entries so far
    ├── project_idea.md                    # Vision + problem statement (read-only)
    ├── project_map.md                     # This file — live structure tracker
    ├── project_structure.md               # Intended architecture blueprint (read-only)
    ├── sprint_tracker.md                  # Live sprint progress tracker
    ├── system_design.md                   # Technical architecture
    └── system_design_doc.md               # Formal system design write-up
```

---

## `Build/` — Live State (after Sprint 2)

```
Build/
└── backend/
    ├── src/
    │   ├── __init__.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py               # pydantic-settings Settings class
    │   │   └── llm_client.py           # get_llm() → ChatDeepSeek (temp param)
    │   ├── db/
    │   │   ├── __init__.py
    │   │   ├── schema.sql              # 6 tables + RLS + pgvector + match_job_skills fn
    │   │   └── client.py              # get_supabase() → Supabase Client (service role)
    │   ├── retrieval/                  # ← Sprint 2
    │   │   ├── __init__.py
    │   │   ├── embeddings.py           # embed_query() — google-genai SDK, 768-dim, RETRIEVAL_QUERY
    │   │   └── vector_store.py         # search_job_skills() — lazy singleton, match_job_skills RPC
    │   ├── prompts/                    # ← Sprint 2
    │   │   └── skill_gap_analyzer.md  # 6-part Amit template for Agent 1 (temp=0.2)
    │   └── agents/
    │       ├── __init__.py
    │       ├── state.py               # SkillBridgeState TypedDict (all agents share)
    │       └── skill_gap/             # ← Sprint 2 — Agent 1
    │           ├── __init__.py
    │           ├── schemas.py         # SkillEntry (with model_validator), SkillGapReport
    │           ├── nodes.py           # analyze_gaps(), safety_net() — inserts skill_gaps row
    │           └── graph.py           # skill_gap_graph = StateGraph compiled (2 nodes)
    ├── scripts/
    │   ├── job_skills_dataset.csv     # 122 rows curated (121 seeded ✅)
    │   └── embed_job_skills.py        # One-time seeding — google-genai SDK, 768-dim MRL
    ├── tests/
    │   ├── unit/
    │   │   ├── test_config.py         # 2/2 ✅ (Sprint 1)
    │   │   ├── test_skill_gap_nodes.py # 9/9 ✅ (Sprint 2)
    │   │   └── test_retrieval.py      # 4/4 ✅ (Sprint 2)
    │   └── integration/
    │       ├── test_db_connection.py  # 4/4 ✅ (Sprint 1)
    │       └── test_skill_gap_e2e.py  # 2/2 ✅ (Sprint 2)
    ├── evals/
    │   └── test_skill_gap.py          # 4 eval tests — gated (RUN_EVALS=1) (Sprint 2)
    ├── conftest.py                    # sys.path fix for src/ imports
    ├── .env.example                   # Secret names (committed)
    ├── .env                           # Real secrets (gitignored)
    ├── .gitignore
    ├── pyproject.toml                 # uv dependencies
    └── requirements.txt               # pip-compiled lock
```

### Supabase — Live DB State

| Table | Rows | Notes |
|---|---|---|
| `profiles` | 0 (test rows cleaned up) | FK anchor for all other tables |
| `skill_gaps` | 0 (test rows cleaned up) | Populated by Agent 1 |
| `learning_plans` | 0 | Populated by Agent 2 (Sprint 3) |
| `quiz_results` | 0 | Populated by Agent 3a/3b (Sprints 4–5) |
| `job_skills` | **121** | Seeded ✅ — 768-dim vectors, IVFFlat index built |
| `weekly_reports` | 0 | Populated by Agent 4 (Sprint 8) |

---

## Update Log

| Date | Change |
|------|--------|
| 2026-07-17 | Created `documentation/sprint_plan/sprint01.md` |
| 2026-07-17 | Created `documentation/sprint_tracker.md` |
| 2026-07-17 | Created `documentation/project_map.md` (this file) |
| 2026-07-17 | Sprint 1: Scaffolded `Build/backend/` — 20 files (pyproject.toml, config.py, llm_client.py, db/client.py, db/schema.sql, agents/state.py, embed_job_skills.py, job_skills_dataset.csv, conftest.py, .env.example, .gitignore, all `__init__.py`, both test files) |
| 2026-07-17 | Sprint 1: All tests passing — unit 2/2 ✅, integration 4/4 ✅, 121 rows seeded ✅ |
| 2026-07-17 | Sprint 2: Created `src/retrieval/` package (`embeddings.py`, `vector_store.py`) |
| 2026-07-17 | Sprint 2: Created `src/agents/skill_gap/` package (`schemas.py`, `nodes.py`, `graph.py`) |
| 2026-07-17 | Sprint 2: Created `src/prompts/skill_gap_analyzer.md` |
| 2026-07-17 | Sprint 2: Created unit tests (13 pass), integration tests (2 pass), evals (gated) |
| 2026-07-17 | Sprint 2: Created `documentation/sprint_plan/sprint02.md` |
| 2026-07-17 | Sprint 2: Closed ✅ — commit `9c06e1c` pushed to GitHub |
| 2026-07-18 | Updated `AGENTS.md` section 8 — frequent commit checkpoints + agent runs git directly |

---

*This file is maintained by the agent. Update after every file/folder change.*
