# SkillBridge — Production Project Structure

> **Project:** SkillBridge — Multi-Agent Adaptive Learning System
> **SDG:** SDG 4 — Quality Education
> **Stack:** SvelteKit (Vercel) · FastAPI on Modal · LangGraph · Supabase · DeepSeek V4 Flash · Resend
> **Skill Applied:** production-project-structure v1.0
> **References:** [project_idea.md](./project_idea.md) · [system_design.md](./system_design.md) · [system_design_doc.md](./system_design_doc.md)

---

## Structure Decision

| Question | Answer |
|---|---|
| **Stack** | SvelteKit (frontend) + FastAPI/Python (backend) — two separate apps |
| **Scale** | Solo developer, MVP, 200 demo users |
| **State** | Greenfield — new project |
| **Pattern** | Hybrid: Template C (AI/RAG) for backend + Feature-Sliced lite for SvelteKit frontend |
| **Org axis** | **Feature-first** inside each app (`agents/`, `api/`, `retrieval/`) — not layer-first |
| **Boundary** | Backend = Python monolith on Modal. Frontend = SvelteKit on Vercel. No monorepo overhead needed at this scale. |

**Chosen pattern:** Two sibling app directories in one repo (`backend/` + `frontend/`), no Turborepo/pnpm
workspaces needed. The two apps share nothing at runtime — they communicate only over HTTPS. A shared
`Planning/` directory for documents lives outside both apps.

> **Principle applied (P5 — Start Flat):** Do not extract a shared `packages/` layer until two independent
> consumers exist. At MVP scale with one frontend and one backend, there are none. Start flat, extract later.

---

## Full Folder Tree

```
skillbridge/                               # Repo root
|
+-- backend/                               # FastAPI app deployed on Modal
|   |
|   +-- src/
|   |   |
|   |   +-- agents/                        # LangGraph StateGraphs — control plane
|   |   |   +-- __init__.py
|   |   |   +-- state.py                   # SkillBridgeState TypedDict (shared by all agents)
|   |   |   |
|   |   |   +-- skill_gap/                 # Agent 1 — Skill Gap Analyzer
|   |   |   |   +-- __init__.py
|   |   |   |   +-- graph.py               # StateGraph definition for Agent 1
|   |   |   |   +-- nodes.py               # Node functions: analyze_gaps, safety_net
|   |   |   |   +-- schemas.py             # Pydantic output schema: SkillGapReport
|   |   |   |
|   |   |   +-- learning_planner/          # Agent 2 — Learning Path Planner
|   |   |   |   +-- __init__.py
|   |   |   |   +-- graph.py               # StateGraph definition for Agent 2
|   |   |   |   +-- nodes.py               # Node functions: plan_milestones
|   |   |   |   +-- schemas.py             # Pydantic output schema: MilestoneList
|   |   |   |
|   |   |   +-- daily_checkin/             # Agent 3a + 3b — Morning Brief + Quiz Conductor
|   |   |   |   +-- __init__.py
|   |   |   |   +-- morning_brief.py       # Agent 3a: cheat sheet generation + Resend delivery
|   |   |   |   +-- quiz_conductor.py      # Agent 3b: MCQ generation, quiz_id, email link
|   |   |   |   +-- quiz_evaluator.py      # Agent 3b eval: score answers, conditional edge
|   |   |   |   +-- replanner.py           # Replanner subgraph: surgical milestone rewrite
|   |   |   |   +-- schemas.py             # Pydantic schemas: QuizQuestion, QuizResult
|   |   |   |
|   |   |   +-- progress_report/           # Agent 4 — Weekly Progress Report
|   |   |       +-- __init__.py
|   |   |       +-- graph.py               # StateGraph for Agent 4
|   |   |       +-- nodes.py               # aggregate_scores, generate_report, linkedin_post
|   |   |       +-- schemas.py             # Pydantic schema: WeeklyReport
|   |   |
|   |   +-- retrieval/                     # RAG data plane — pgvector pipeline
|   |   |   +-- __init__.py
|   |   |   +-- embeddings.py              # gemini-embedding-001 client: embed query + dataset
|   |   |   +-- vector_store.py            # pgvector cosine search adapter (Supabase)
|   |   |
|   |   +-- prompts/                       # Versioned prompt templates (Amit 6-part format)
|   |   |   +-- skill_gap_analyzer.md      # Agent 1 prompt: Persona|Goal|Context|Task|Rules|Constraints
|   |   |   +-- learning_planner.md        # Agent 2 prompt
|   |   |   +-- morning_brief.md           # Agent 3a prompt (temp=0.7)
|   |   |   +-- quiz_generator.md          # Agent 3b MCQ generation prompt (temp=0.3)
|   |   |   +-- quiz_evaluator.md          # Agent 3b evaluation prompt (temp=0)
|   |   |   +-- replanner.md               # Replanner prompt (temp=0.3)
|   |   |   +-- progress_report.md         # Agent 4 prompt + LinkedIn post (temp=0.8)
|   |   |
|   |   +-- api/                           # FastAPI HTTP serving layer
|   |   |   +-- __init__.py
|   |   |   +-- main.py                    # FastAPI app instantiation + router registration
|   |   |   +-- deps.py                    # Shared dependencies: supabase client, auth JWT check
|   |   |   +-- routers/
|   |   |       +-- __init__.py
|   |   |       +-- analyze.py             # POST /analyze  -> triggers Agent 1
|   |   |       +-- plan.py                # POST /plan     -> triggers Agent 2
|   |   |       +-- quiz.py                # GET  /quiz/{quiz_id} + POST /submit
|   |   |       +-- report.py              # GET  /report/{user_id} -> triggers Agent 4
|   |   |
|   |   +-- email/                         # Resend email delivery
|   |   |   +-- __init__.py
|   |   |   +-- client.py                  # Resend SDK wrapper
|   |   |   +-- templates/
|   |   |       +-- morning_brief.html     # HTML template: cheat sheet email
|   |   |       +-- quiz_link.html         # HTML template: quiz link email
|   |   |       +-- quiz_result.html       # HTML template: pass / review result email
|   |   |       +-- weekly_report.html     # HTML template: Sunday digest email
|   |   |
|   |   +-- db/                            # Supabase database layer
|   |   |   +-- __init__.py
|   |   |   +-- client.py                  # supabase-py async client singleton
|   |   |   +-- schema.sql                 # Source-of-truth SQL migrations
|   |   |
|   |   +-- core/                          # Cross-cutting infrastructure
|   |       +-- __init__.py
|   |       +-- config.py                  # All env vars via pydantic-settings (Modal secrets)
|   |       +-- llm_client.py              # DeepSeek V4 Flash client: langchain-deepseek wrapper
|   |       +-- observability.py           # LangSmith tracer setup (LANGCHAIN_TRACING_V2)
|   |
|   +-- crons/                             # Modal scheduled functions (cron entry points)
|   |   +-- __init__.py
|   |   +-- morning_brief_cron.py          # Cron: 0 2 * * * (7:30 AM IST)
|   |   +-- quiz_conductor_cron.py         # Cron: 30 10 * * * (4:00 PM IST)
|   |   +-- weekly_report_cron.py          # Cron: 30 13 * * 0 (Sunday 7 PM IST)
|   |
|   +-- scripts/                           # One-time setup scripts (not production code)
|   |   +-- embed_job_skills.py            # Embeds job_skills dataset via gemini-embedding-001
|   |
|   +-- evals/                             # Agent quality evaluations (CI-runnable)
|   |   +-- fixtures/
|   |   |   +-- golden_quiz_dataset.json   # 10 reference topic->expected_mcq pairs
|   |   +-- test_skill_gap.py              # Eval: Agent 1 output schema + readiness range
|   |   +-- test_quiz_generation.py        # Eval: Agent 3b MCQ format correctness
|   |   +-- test_replanner.py              # Eval: replanner output is valid MilestoneList
|   |
|   +-- tests/
|   |   +-- unit/
|   |   |   +-- test_replanner_logic.py    # Unit: surgical splice logic
|   |   |   +-- test_scoring.py            # Unit: score >= 70 route, < 70 route
|   |   +-- integration/
|   |       +-- test_api_endpoints.py      # Integration: /analyze -> /plan -> /quiz
|   |
|   +-- modal_app.py                       # Modal entry point: FastAPI ASGI + 3 crons
|   +-- pyproject.toml                     # Python dependencies (uv or poetry)
|   +-- .env.example                       # Template for local dev secrets (never commit .env)
|   +-- README.md
|
+-- frontend/                              # SvelteKit app deployed on Vercel
|   |
|   +-- src/
|   |   +-- app.html                       # Root HTML shell
|   |   +-- app.css                        # Global Tailwind CSS + custom tokens
|   |   |
|   |   +-- routes/                        # SvelteKit file-based routing
|   |   |   +-- +layout.svelte             # Root layout: auth check, nav
|   |   |   +-- +layout.server.js          # Auth session load (Supabase session)
|   |   |   +-- +page.svelte               # / Landing page (SSR)
|   |   |   |
|   |   |   +-- login/
|   |   |   |   +-- +page.svelte           # /login  Google OAuth (SSR)
|   |   |   |
|   |   |   +-- onboarding/
|   |   |   |   +-- +page.svelte           # /onboarding  Goal + skills form (SSR)
|   |   |   |   +-- +page.server.js        # Form action: POST /analyze -> POST /plan
|   |   |   |
|   |   |   +-- dashboard/
|   |   |   |   +-- +page.svelte           # /dashboard  Progress + LinkedIn post card (SSR)
|   |   |   |   +-- +page.server.js        # Load milestones + weekly report from Supabase
|   |   |   |
|   |   |   +-- quiz/
|   |   |   |   +-- +page.svelte           # /quiz  5 MCQ quiz (CLIENT-ONLY: ssr=false)
|   |   |   |   +-- +page.js               # export const ssr = false
|   |   |   |
|   |   |   +-- results/
|   |   |       +-- +page.svelte           # /results  Score + feedback (SSR)
|   |   |       +-- +page.server.js        # Load quiz result from Supabase
|   |   |
|   |   +-- lib/                           # SvelteKit $lib alias — shared utilities
|   |       +-- components/                # Reusable UI components (presentational only)
|   |       |   +-- MilestoneCard.svelte
|   |       |   +-- ProgressBar.svelte
|   |       |   +-- LinkedInPostCard.svelte
|   |       |   +-- QuizOption.svelte
|   |       |
|   |       +-- api/                       # FastAPI HTTP client wrappers (data-access only)
|   |       |   +-- analyze.js             # fetch POST /analyze
|   |       |   +-- quiz.js                # fetch GET /quiz/{id} + POST /submit
|   |       |   +-- report.js              # fetch GET /report/{user_id}
|   |       |
|   |       +-- supabase.js                # Supabase client (anon key + SSR helper)
|   |       +-- utils.js                   # Pure utilities: formatDate, slugify
|   |
|   +-- static/
|   |   +-- favicon.png
|   |
|   +-- package.json
|   +-- svelte.config.js                   # Vercel adapter config
|   +-- vite.config.js
|   +-- tailwind.config.js
|   +-- postcss.config.js
|   +-- .env.example                       # VITE_API_URL + SUPABASE_ANON_KEY (safe to expose)
|
+-- Planning/                              # Project planning documents (not deployed)
|   +-- project_idea.md
|   +-- system_design.md
|   +-- system_design_doc.md
|   +-- project_structure.md              # <- This file
|
+-- .gitignore                             # .env, __pycache__, .svelte-kit, node_modules
+-- .github/
|   +-- workflows/
|       +-- ci.yml                         # Run evals + frontend build check on PR
+-- README.md
```

---

## Directory-by-Directory Rationale

### `backend/src/agents/`

**Pattern:** Feature-first at the top level, consistent layer structure inside each agent.

Each agent is an isolated Python package. An external caller (FastAPI router or Modal cron) imports
only from the agent package — never from internal files. This enforces the **barrel file rule**:

```python
# Good — imports from package boundary
from src.agents.skill_gap import run_skill_gap_analysis

# Bad — reaches into internals
from src.agents.skill_gap.nodes import _build_prompt
```

`state.py` at the top of `agents/` is **shared by all agents** — the `SkillBridgeState` TypedDict
is the single memory contract for the LangGraph graph. It lives here (not in `core/`) because it
is an agent concern, not an infrastructure concern.

---

### `backend/src/retrieval/`

**Pattern:** RAG data plane, separated from the control plane (agents).

This directory implements only **retrieval mechanics** — embedding a query and performing cosine
search via pgvector. It has no knowledge of agents, prompts, or LangGraph state.
Agent 1 calls `retrieval.vector_store.search()` — the dependency arrow points
agent → retrieval, never the reverse.

---

### `backend/src/prompts/`

**Rule:** Prompts are **versioned artifacts**, not inline strings.

Every prompt is a `.md` file loaded at agent startup. This means:
- Prompt changes are Git-diffable.
- Prompts can be swapped without code changes.
- The Amit Tiwari 6-part structure (Persona · Goal · Context · Task · Field Rules · Constraints)
  is enforced by convention in each file.

```python
# How prompts are loaded in nodes.py
from pathlib import Path
PROMPT = (Path(__file__).parent.parent.parent / "prompts" / "skill_gap_analyzer.md").read_text()
```

---

### `backend/src/api/routers/`

**Pattern:** One router file per HTTP resource. Routers do **no business logic** — they validate
input (Pydantic), call the agent, and return the response.

```python
# api/main.py
from src.api.routers import analyze, plan, quiz, report

app = FastAPI()
app.include_router(analyze.router, prefix="/analyze")
app.include_router(plan.router,    prefix="/plan")
app.include_router(quiz.router,    prefix="/quiz")
app.include_router(report.router,  prefix="/report")
```

---

### `backend/crons/`

**Pattern:** Cron entry points are thin wrappers — they collect active users from Supabase and
dispatch to the relevant agent via `asyncio.gather`. The Modal cron knows only the agent entrypoint.
This means cron and HTTP paths share the same agent code — tested once, reused twice.

```python
# crons/morning_brief_cron.py
@app.function(schedule=modal.Cron("0 2 * * *"))
async def morning_brief_cron():
    from src.agents.daily_checkin.morning_brief import run_for_all_users
    await run_for_all_users()
```

---

### `backend/evals/`

**Rule:** Eval datasets are checked-in fixtures — never modified without a PR.

These are **quality gates** that verify agent output correctness, not pytest unit tests:

| File | What it asserts |
|---|---|
| `test_skill_gap.py` | Agent 1 output matches `SkillGapReport` schema; readiness in 0-100 |
| `test_quiz_generation.py` | Agent 3b produces exactly 5 questions with 4 options each |
| `test_replanner.py` | Replanner output is valid `MilestoneList`; length = failed + next only |

Run in CI (`ci.yml`) on every PR against the golden fixtures in `evals/fixtures/`.

---

### `frontend/src/routes/`

**Pattern:** SvelteKit file-based routing — one folder per page.

| Route | Rendering | Why |
|---|---|---|
| `/` | SSR | Landing page: fast first paint + SEO |
| `/login` | SSR | Google OAuth redirect handled server-side |
| `/onboarding` | SSR | Form action calls FastAPI — server-side submit |
| `/dashboard` | SSR | Reads Supabase session + milestones on server |
| `/quiz` | CSR (`ssr=false`) | Pure client interaction; no server secrets needed |
| `/results` | SSR | Score loaded from Supabase after redirect |

The `/quiz` page is the **only** client-only route. Quiz state is keyed by `quiz_id` from the
URL param, so no session secret is ever exposed in the browser.

---

### `frontend/src/lib/`

**Pattern:** Three sub-categories with strict one-directional import rules:

| Directory | Type | Rule |
|---|---|---|
| `lib/components/` | UI (presentational) | No data fetching. Props in, events out. |
| `lib/api/` | Data-access | Wraps `fetch` calls to FastAPI. No UI imports. |
| `lib/supabase.js` | Data-access | Supabase client singleton. No UI imports. |
| `lib/utils.js` | Util | Pure functions only. No imports from above. |

This mirrors the Four Library Types: `ui → data-access → util`. No reverse dependencies.

---

## Module Boundary Rules

1. **No cross-agent imports.** `agents/skill_gap/` must not import from `agents/learning_planner/`.
   LangGraph wires them via the shared `state.py` — never via direct Python imports.

2. **No agent imports from `api/`.** The `api/routers/` layer calls agents; agents never call routers.

3. **`core/` is infrastructure only.** `core/llm_client.py` and `core/config.py` may be imported
   by anyone. They must never import from `agents/`, `api/`, or `retrieval/`.

4. **`prompts/` files are pure text.** No Python logic in prompt files. Load via `Path.read_text()`.

5. **`evals/` and `tests/` never imported by `src/`.** One-directional only.

6. **Frontend `lib/components/` must not call `fetch`.** All network calls go through `lib/api/`.

---

## Naming Conventions

### Backend (Python)

| Item | Convention | Example |
|---|---|---|
| Package directories | `snake_case` | `skill_gap/`, `daily_checkin/` |
| Python files | `snake_case.py` | `quiz_conductor.py` |
| Pydantic schemas | `PascalCase` | `SkillGapReport`, `MilestoneList` |
| LangGraph state | `PascalCase` + `State` suffix | `SkillBridgeState` |
| Prompt files | `snake_case.md` | `skill_gap_analyzer.md` |
| Node functions | `snake_case` verbs | `analyze_gaps()`, `plan_milestones()` |
| Cron functions | `snake_case` + `_cron` suffix | `morning_brief_cron` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `DEEPSEEK_API_KEY` |

### Frontend (Svelte / JS)

| Item | Convention | Example |
|---|---|---|
| Svelte components | `PascalCase.svelte` | `MilestoneCard.svelte` |
| Route folders | `kebab-case` | `quiz/`, `results/` |
| JS utilities | `camelCase` | `formatDate()`, `slugify()` |
| API wrapper files | `camelCase.js` | `analyze.js`, `quiz.js` |
| CSS custom properties | `--kebab-case` | `--color-primary`, `--spacing-md` |

---

## Secret Management

| Secret | Where stored | Who reads it |
|---|---|---|
| `DEEPSEEK_API_KEY` | Modal secret store | `core/llm_client.py` |
| `GEMINI_API_KEY` | Modal secret store | `retrieval/embeddings.py` (setup only) |
| `SUPABASE_URL` | Modal secret store | `db/client.py` |
| `SUPABASE_SERVICE_KEY` | Modal secret store | `db/client.py` (bypasses RLS for crons) |
| `RESEND_API_KEY` | Modal secret store | `email/client.py` |
| `LANGSMITH_API_KEY` | Modal secret store | `core/observability.py` |
| `VITE_API_URL` | Vercel env var | `frontend/src/lib/api/*.js` |
| `SUPABASE_ANON_KEY` | Vercel env var | `frontend/src/lib/supabase.js` |

**Rule:** All Modal secrets are read via `core/config.py` (pydantic-settings) — never accessed
directly in agent or router code.

---

## Build and Deployment Targets

| Target | Command | Deploys to |
|---|---|---|
| Backend | `modal deploy modal_app.py` | Modal (FastAPI ASGI + 3 crons) |
| Frontend | `git push origin main` | Vercel (auto-deploy) |
| Schema | SQL via Supabase dashboard | Supabase PostgreSQL |
| Dataset | `python scripts/embed_job_skills.py` | `job_skills` table (one-time) |

### Local Development

```bash
# Backend
cd backend
modal serve modal_app.py               # Local tunnel on port 8000 (hot-reload)
modal run crons/morning_brief_cron.py  # Test a single cron manually

# Frontend
cd frontend
npm run dev                            # SvelteKit HMR on port 5173
```

---

## Three Most Important First Steps

1. **`backend/src/core/config.py` first** — set up pydantic-settings with all env var names.
   Every module will need this. Do it before writing a single agent node.

2. **`backend/src/prompts/` directory next** — create all 7 prompt `.md` files with Amit's
   6-part structure skeleton. Establish the pattern before writing agent nodes.

3. **`backend/scripts/embed_job_skills.py` + `evals/fixtures/golden_quiz_dataset.json`** — seed
   the jobs dataset and golden eval fixtures before Agent 1 can be meaningfully tested.

---

## Evolution Path

| When | Action |
|---|---|
| >30 active students | Upgrade Resend to Starter ($20/mo) |
| >50 concurrent cron users | Add `asyncio.Semaphore(10)` to throttle DeepSeek burst |
| >200 active students | Enable Supabase read replicas |
| >1M job_skills rows | Migrate `retrieval/vector_store.py` to Qdrant |
| Second frontend app added | Extract `lib/api/` into a shared `packages/api-client/` |
| Multiple developers | Add `.github/CODEOWNERS` assigning `backend/src/agents/` per agent owner |

---

*Generated: 2026-07-17*
*Skill: production-project-structure | Pattern: AI/RAG Template C + Feature-Sliced lite (SvelteKit)*
*Project: SkillBridge — AICTE AI Automation & Intelligent Solutions, IBM SkillsBuild 2026*
