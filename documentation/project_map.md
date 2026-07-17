# SkillBridge — Live Project Map

> **Purpose:** Tracks the *actual* file/folder state of the repository as it is built.
> Update every time a file or folder is added, deleted, or renamed.
> Do NOT confuse with `project_structure.md` (the original plan).

*Last updated: 2026-07-17 — Sprint 1 in progress; all code files built, awaiting Supabase schema apply + .env fill + seed run*

---

## Repository Root

```
F:\IBM internship\sunmission\Project\
├── AGENTS.md                              # Behavioral guidelines
├── Build/                                 # (empty — Sprint 1 will scaffold this)
├── Planning/                              # Alias / symlink directory (mirrors documentation/)
└── documentation/
    ├── plan/
    │   └── implementation_plan.md         # Master 10-sprint roadmap
    ├── sprint_plan/
    │   └── sprint01.md                    # Sprint 1 detailed task plan ← NEW
    ├── project_idea.md                    # Vision + problem statement (read-only)
    ├── project_structure.md               # Intended architecture blueprint (read-only)
    ├── sprint_tracker.md                  # Live sprint progress tracker ← NEW
    ├── system_design.md                   # Technical architecture
    └── system_design_doc.md               # Formal system design write-up
```

---

## `Build/` (target state after Sprint 1)

```
Build/
└── backend/
    ├── src/
    │   ├── __init__.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py               # pydantic-settings Settings class
    │   │   └── llm_client.py           # get_llm() → ChatDeepSeek
    │   ├── db/
    │   │   ├── __init__.py
    │   │   ├── schema.sql              # 6 tables + RLS + pgvector + match_job_skills fn
    │   │   └── client.py              # get_supabase() → Supabase Client
    │   └── agents/
    │       ├── __init__.py
    │       └── state.py               # SkillBridgeState TypedDict
    ├── scripts/
    │   ├── job_skills_dataset.csv     # Manually curated 100+ rows
    │   └── embed_job_skills.py        # One-time embedding + insert script
    ├── tests/
    │   ├── unit/
    │   │   └── test_config.py         # 2 unit tests
    │   └── integration/
    │       └── test_db_connection.py  # 4 integration tests
    ├── .env.example                   # Secret names (committed)
    ├── .env                           # Real secrets (gitignored)
    ├── .gitignore
    └── pyproject.toml                 # uv dependencies
```

| 2026-07-17 | Scaffolded `Build/backend/` — 20 files created (pyproject.toml, config.py, llm_client.py, db/client.py, db/schema.sql, agents/state.py, scripts/embed_job_skills.py, scripts/job_skills_dataset.csv [122 rows], conftest.py, .env.example, .gitignore, all __init__.py files, both test files) |
| 2026-07-17 | Unit tests passing: `tests/unit/test_config.py` — 2/2 ✅ |
| 2026-07-17 | **Awaiting user:** fill `.env`, apply `schema.sql` in Supabase, run `embed_job_skills.py`, run integration tests |

---

## Update Log

| Date | Change |
|------|--------|
| 2026-07-17 | Created `documentation/sprint_plan/sprint01.md` |
| 2026-07-17 | Created `documentation/sprint_tracker.md` |
| 2026-07-17 | Created `documentation/project_map.md` (this file) |

---

*This file is maintained by the agent. Update after every file/folder change.*
