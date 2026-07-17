# SkillBridge — Multi-Agent Adaptive Learning System

**SDG:** SDG 4 — Quality Education
**Internship:** AICTE AI Automation & Intelligent Solutions — IBM SkillsBuild 2026
**Submission Deadline:** 20th July 2026
**Elevator Pitch:** "Duolingo + ChatGPT + a personal career coach — for any Indian student, for any skill, for free. It does not just tell you what to learn. It rewrites your plan when you fall behind."

---

## The Problem (3 Real Pain Points)

1. **No personalization at scale:** College curricula are one-size-fits-all. A student who excels at algorithms but struggles at system design gets the same syllabus as everyone else.
2. **Career-skill disconnect:** 65% of engineering graduates in India are unemployable (NASSCOM 2025) — they finish degrees without knowing which specific skills hiring teams actually want.
3. **No action-taking guidance:** ChatGPT can tell you what to learn. It cannot monitor your progress, send you a morning cheat sheet, conduct an afternoon test, adapt your plan based on performance, and update your roadmap when you fall behind.

> Existing alternatives: YouTube, Coursera, ChatGPT, LinkedIn Learning, Guidopia, IraConnect — all generate static plans. None take daily action. None adapt.

---

## Why This Solves a REAL Problem (SDG 4 Alignment)

- **NEP 2020** mandates skill-based education — SkillBridge operationalises this at zero cost.
- **NASSCOM 2025 data:** 65% employability gap — SkillBridge maps learning directly to real job requirements.
- **India-first design:** Free resources only, WhatsApp/email-first, no paywall, works on any device.
- **SDG 4 targets:** 4.4 (increase skills for employment) + 4.5 (equal access to quality education).

---

## The Solution — What SkillBridge Does

A **multi-agent LangGraph system** with 2 core agents — all 4 agent properties satisfied:

| Property | How SkillBridge satisfies it |
|----------|------------------------------|
| **Perception** | Reads user goal, current skills, study schedule + quiz responses |
| **Reasoning** | DeepSeek V4 Flash analyzes gaps, plans milestones, evaluates test answers |
| **Acting** | Sends morning cheat sheet email, sends quiz link, rewrites learning plan |
| **Learning** | Adapts the entire roadmap when quiz score is below threshold (self-correction loop) |

---

## The Daily Learning Flow (Core Innovation)

This is the feature that no competitor has. SkillBridge fits inside a student's real day:

```
EVENING (5:00 PM - 9:00 PM IST)
  Student studies today's topic from their personalized learning plan
  (YouTube videos, free resources assigned by Agent 2)

MORNING (7:30 AM IST) — Modal Cron fires
  Agent 3a: Morning Brief Generator
    - Reads today's milestone topic from Supabase
    - DeepSeek V4 Flash generates a concise cheat sheet:
        * 5 key concepts
        * 2 common misconceptions
        * 1 mnemonic or memory trick
        * 3 practice questions to think about
    - Resend delivers a polished HTML "morning brief" newsletter
    - Student reads it over breakfast / on the way to school

AFTERNOON (4:00 PM IST) — Modal Cron fires
  Agent 3b: Test Conductor
    - Resend delivers a "Your Daily Test is Ready" email
    - Email contains a direct link to /quiz route in SvelteKit app
    - Student clicks link -> 5 MCQs on today's topic (no Google Forms dependency)
    - Student submits -> POST to FastAPI on Modal
    - LangGraph evaluates answers (DeepSeek, temperature=0)
    - Conditional edge decision:
        score >= 70  ->  Mark milestone complete, advance to next topic
        score <  70  ->  Replanner subgraph rewrites the affected milestones
    - Result + personalized feedback email sent via Resend
    - All scores + plan changes logged to Supabase

WEEKLY (Sunday evening)
  Agent 4: Progress Report Agent
    - Reads all milestone statuses from Supabase
    - Generates progress report + motivational summary
    - Sends polished weekly digest email
    - DeepSeek crafts a personalized LinkedIn celebration post for the completed milestone
    - Post displayed in dashboard with a one-click "Copy & Post" button
    - Student pastes to LinkedIn manually — the WOW is the AI-crafted content, not auto-posting
    [Note: LinkedIn Partner API requires weeks of approval; this design is honest and still impressive]
```

---

## Agent Architecture (LangGraph StateGraph)

```
User Onboarding (SvelteKit form)
  goal + current_skills + hours_per_week + study_start_time
        |
        v
[Agent 1: Skill Gap Analyzer]
  - pgvector RAG retrieves job requirements from Supabase jobs dataset
  - Compares user skills vs. target role requirements
  - Hard safety net: overall_readiness < 20% -> auto-extend timeline to 6 months
  - DeepSeek V4 Flash, temperature=0.2, Structured Output Parser
  - Outputs: structured skill_gap_report (JSON) -> saved to Supabase
        |
        v
[Agent 2: Learning Path Planner]
  - Decomposes skill gaps into weekly milestones
  - Each milestone has: topic, daily_subtopics[], free_resources[]
  - Assigns free resources only (YouTube, Coursera free, GitHub repos)
  - Sets realistic timelines based on hours_per_week
  - DeepSeek V4 Flash, temperature=0.2
  - Outputs: full learning_plan (JSON) -> saved to Supabase
        |
        v
[Agent 3: Daily Check-In Agent] — triggered by two Modal crons
  3a. Morning Brief (7:30 AM IST)
    - Reads current milestone topic from Supabase
    - Generates cheat sheet (DeepSeek, temperature=0.7 for creativity)
    - Sends HTML email via Resend
  3b. Test Conductor (4:00 PM IST)
    - Generates 5 MCQs for today's topic (DeepSeek, temperature=0.3)
    - Saves quiz to Supabase with unique quiz_id
    - Sends quiz link email via Resend -> student visits /quiz?id={quiz_id}
    - Student submits answers -> FastAPI -> LangGraph evaluates
    - Conditional edge: advance | replan
    - Logs to Supabase: quiz_results table
        |
        v
[Agent 4: Progress Report Agent] — Sunday Modal cron
  - Aggregates week's quiz scores and milestone completions from Supabase
  - Generates motivational progress report
  - Sends HTML weekly digest via Resend
  - Generates celebratory LinkedIn post text via DeepSeek (thinking mode, temperature=0.8)
  - Post stored in Supabase + surfaced in dashboard with "Copy & Post" button
  - WOW factor: the AI writes a post that actually sounds human — evaluators can read it live
```

---

## LangGraph State (Shared Memory)

```python
from typing import TypedDict, List, Optional

class SkillBridgeState(TypedDict):
    # User profile
    user_id: str
    user_goal: str               # "Get a backend dev job at a startup"
    current_skills: List[str]    # ["Python basics", "HTML/CSS"]
    hours_per_week: int          # 10

    # Agent 1 outputs
    skill_gap_report: dict       # {skills: [{name, gap_score, priority}], readiness_percent}

    # Agent 2 outputs
    learning_plan: List[dict]    # [{milestone, topic, daily_subtopics, resources, week}]
    current_milestone_index: int

    # Agent 3 state
    todays_topic: str
    current_quiz_id: str
    quiz_scores: List[float]     # history of all daily scores
    plan_revision_count: int     # number of times plan was rewritten

    # Logging
    progress_log: List[str]      # timestamped entries for LangSmith + Supabase
```

---

## Supabase Schema

```sql
-- Users (managed by Supabase Auth + Google OAuth)
-- auth.users is auto-created by Supabase

-- Student profiles
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  user_goal TEXT NOT NULL,
  current_skills TEXT[] NOT NULL,
  hours_per_week INT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Skill gap analysis results
CREATE TABLE skill_gaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  report JSONB NOT NULL,          -- full gap report from Agent 1
  overall_readiness INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated learning plans
CREATE TABLE learning_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  milestones JSONB NOT NULL,      -- full plan from Agent 2
  current_milestone_index INT DEFAULT 0,
  revision_count INT DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily quiz results
CREATE TABLE quiz_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  quiz_id TEXT UNIQUE NOT NULL,
  topic TEXT NOT NULL,
  questions JSONB NOT NULL,       -- the 5 MCQs
  answers JSONB,                  -- student's submitted answers
  score FLOAT,
  feedback TEXT,
  recommendation TEXT,            -- "advance" | "review"
  sent_at TIMESTAMPTZ,
  submitted_at TIMESTAMPTZ
);

-- Jobs dataset for RAG (pgvector)
CREATE TABLE job_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role TEXT NOT NULL,
  skill TEXT NOT NULL,
  importance_level INT,           -- 1-5
  embedding vector(1536)          -- pgvector for RAG retrieval
);
```

---

## Why This Wins (Evaluation Criteria)

| Criterion | Typical submission | SkillBridge |
|-----------|-------------------|-------------|
| Agent properties | 1-2 of 4 | All 4: Perception, Reasoning, Acting, Learning |
| Multi-agent | Single agent | 4 specialized agents with clean handoffs |
| RAG | None | pgvector over curated jobs dataset (Supabase) |
| Self-correction | None | Quiz fail -> LangGraph rewrites milestones |
| Daily action | None | Morning cheat sheet + afternoon test — every single day |
| Structured output | Random | Structured Output Parser on every agent node |
| Prompt engineering | Ad-hoc | Amit's 6-part template on every prompt |
| Hard safety nets | None | Score thresholds + readiness guards |
| Deployment | Screenshot | Live Vercel URL + Modal backend + LangSmith traces |
| Wow factor | "It sends an email" | "It sends me a cheat sheet at breakfast and tests me after school" |
| SDG alignment | Surface-level | NEP 2020 + SDG 4.4/4.5 + NASSCOM 2025 data |
| Lean Canvas | Missing | Fully filled, PDF-ready |

---

## Tech Stack (All Decisions Final)

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **Frontend** | SvelteKit + Tailwind CSS | Hybrid SSR, compiler-first, exceptional performance, Vercel deploy |
| **Rendering** | Hybrid SSR (SSR default, /quiz client-only) | Dashboard SSR for auth + fast load; quiz page client-only for interactivity |
| **Backend** | FastAPI (Python) on Modal | Python-native, no sleep issues, $30/mo free credits, modal deploy |
| **Scheduling** | Modal cron (@app.function with schedule) | Replaces APScheduler + Render; never sleeps, always fires |
| **LLM** | DeepSeek V4 Flash (langchain-deepseek) | Paid key = no rate limits; 1M context; thinking mode for plan rewrites |
| **Agent orchestration** | LangGraph (StateGraph + conditional edges) | Industry standard, persistent state via Supabase checkpointer |
| **Database** | Supabase (PostgreSQL) | Relational structure for agent state, RLS for security |
| **RAG** | pgvector (Supabase extension) | RAG inside existing DB — no Qdrant needed |
| **Embeddings** | `gemini-embedding-001` (Google AI) | Free tier, 1536-dim output (matches schema), used once to embed jobs dataset |
| **Auth** | Supabase Auth + Google OAuth | One-click login, JWT sessions, zero password handling |
| **Email** | Resend (HTML templates) | Permanent free tier (3,000/mo), best DX, replaces Gmail node |
| **Tracing** | LangSmith | Agent reasoning screenshots for PPT evidence |
| **Frontend host** | Vercel | Auto-deploy from GitHub, free hobby tier |
| **Cost** | ~$0/month | Modal $30 free credits >> actual usage at demo scale |

---

## Prompt Engineering (Amit Tiwari's 6-Part Template)

### Agent 1 — Skill Gap Analyzer

```
Persona: You are a career skills analyst specializing in the Indian tech job market.

Goal: Identify exact skill gaps between a student's current abilities and their target role.

Context:
- Student goal: {{user_goal}}
- Current skills: {{current_skills}}
- Retrieved job market data: {{rag_context}}
- Current timestamp: {{now}}

Task:
- List the top 5-8 skills required for {{user_goal}} from retrieved job data
- Score student's current level (0-100) for each skill
- Calculate gap score (required_level - current_level)
- Prioritize by gap score, highest first

Field Rules:
Return JSON: {
  "skills": [{"name", "required_level", "current_level", "gap_score", "priority"}],
  "overall_readiness_percent": int,
  "recommended_timeline_weeks": int
}

Constraints:
- Do not invent skills not in retrieved job data
- No commentary or markdown outside JSON
- Temperature: 0.2
```

### Agent 3a — Morning Brief Generator

```
Persona: You are a brilliant study coach who creates memorable, scannable cheat sheets.

Goal: Create a 2-minute morning review brief for a student on today's study topic.

Context:
- Topic: {{todays_topic}}
- Milestone context: {{milestone_description}}
- Current timestamp: {{now}} (morning, student is having breakfast)

Task:
- Write exactly 5 key concepts (one sentence each)
- Write 2 common misconceptions students have about this topic
- Write 1 mnemonic or memory trick
- Write 3 quick questions to think about during the day

Field Rules:
Return JSON: {
  "key_concepts": [string x5],
  "misconceptions": [string x2],
  "mnemonic": string,
  "think_about": [string x3]
}

Constraints:
- Friendly, encouraging tone — student is starting their day
- Each concept under 20 words
- Temperature: 0.7 (creative but accurate)
```

### Agent 3b — Quiz Evaluator

```
Persona: You are a strict but fair examiner for technical skills assessment.

Goal: Evaluate a student's quiz answers and decide whether to advance or replan.

Context:
- Topic: {{todays_topic}}
- Questions and correct answers: {{quiz_qa}}
- Student's submitted answers: {{student_answers}}
- Current timestamp: {{now}}

Task:
- Score each answer (correct/incorrect)
- Calculate overall score (0-100)
- Write one-sentence feedback per question
- Recommend "advance" if score >= 70, "review" if score < 70

Field Rules:
Return JSON: {
  "per_question": [{"question_id", "correct", "feedback"}],
  "overall_score": float,
  "summary_feedback": string,
  "recommendation": "advance" | "review"
}

Constraints:
- Temperature: 0 (deterministic scoring, no creativity)
- Do not be lenient — accuracy matters for actual learning
```

---

## Modal Deployment Pattern

```python
import modal
from fastapi import FastAPI

app = modal.App("skillbridge")

# FastAPI web endpoint — always available
@app.function()
@modal.asgi_app()
def fastapi_app():
    from api.main import app as fastapi_app
    return fastapi_app

# Morning cheat sheet — 7:30 AM IST daily (IST = UTC+5:30 -> 2:00 AM UTC)
@app.function(schedule=modal.Cron("0 2 * * *"))
def send_morning_brief():
    from agents.morning_brief import run
    run()

# Afternoon quiz link — 4:00 PM IST daily (IST = UTC+5:30 -> 10:30 AM UTC)
@app.function(schedule=modal.Cron("30 10 * * *"))
def send_quiz_link():
    from agents.quiz_conductor import send_links
    send_links()

# Weekly progress report — Sunday 7:00 PM IST (1:30 PM UTC)
@app.function(schedule=modal.Cron("30 13 * * 0"))
def weekly_report():
    from agents.progress_report import run
    run()
```

---

## SvelteKit Route Structure

```
src/
  routes/
    +page.svelte              # Landing page (SSR)
    +layout.svelte            # Root layout with auth check
    login/
      +page.svelte            # Google OAuth login (SSR)
    onboarding/
      +page.svelte            # Goal + skills form (SSR)
      +page.server.js         # Calls FastAPI /analyze on submit
    dashboard/
      +page.svelte            # Progress dashboard (SSR)
      +page.server.js         # Loads milestones from Supabase
    quiz/
      +page.svelte            # Quiz page (client-only, ssr=false)
      +page.js                # export const ssr = false
    results/
      +page.svelte            # Quiz result + feedback (SSR)
```

---

## Lean Canvas (Submission-Ready)

| Section | Content |
|---------|---------|
| **Problem** | 1. No personalization in education 2. 65% employability gap (NASSCOM 2025) 3. No action-taking guidance — ChatGPT advises, never adapts |
| **Existing Alternatives** | YouTube, Coursera, ChatGPT, Guidopia, IraConnect — all static, no daily action |
| **Customer Segments** | Primary: Indian engineering students (18-22). Early adopters: Final-year students in placement prep |
| **Unique Value Proposition** | "The only free learning system that sends you a cheat sheet at breakfast, tests you after school, and rewrites your plan when you fail." |
| **Solution** | 1. AI skill gap analysis vs real job data 2. Daily morning cheat sheet + afternoon test 3. Self-correcting roadmap that adapts when you struggle |
| **Unfair Advantage** | Student building for students — knows exactly which free resources work; India-specific job market data; zero-cost stack |
| **Revenue Streams** | B2C: Premium tier (resume review, mock interviews). B2B: College placement cell licenses. Additional: Corporate upskilling |
| **Cost Structure** | Tech: DeepSeek API (~$2/mo at demo scale), Supabase free, Modal free credits, Vercel free, Resend free |
| **Key Metrics** | Daily active learners, morning email open rate, quiz completion rate, plan adaptation rate, milestone completion rate |
| **Channels** | Acquisition: LinkedIn, college placement cells, student WhatsApp groups. Distribution: Web app, email |

---

## Project PPT Structure (Shark Tank Style)

Per Amit's advice: "Imagine you are pitching to investors on Shark Tank."

1. **Title** — SkillBridge | Team | SDG 4
2. **Problem** — 65% unemployability gap visual + "ChatGPT gives advice. Nobody takes action."
3. **Existing Alternatives** — Why they all fail (static, not adaptive)
4. **Solution** — The daily flow diagram (5pm study → 7:30am brief → 4pm test → replan)
5. **Unique Value Proposition** — "The only system that rewrites your plan when you fail"
6. **Agent Architecture** — LangGraph state diagram (4 agents + conditional edges)
7. **Demo** — Live walkthrough: onboard → plan → morning email → quiz → fail → plan adapts
8. **Tech Stack** — SvelteKit + FastAPI + Modal + Supabase + DeepSeek + Resend
9. **SDG Alignment** — SDG 4.4 + 4.5 + NEP 2020 + NASSCOM 2025
10. **Lean Canvas** — One-pager (submit separately as PDF)
11. **Team** — Members and roles

---

## Deployment Checklist

### Phase 1 — Backend Core
- [ ] Set up Supabase project: create schema (profiles, skill_gaps, learning_plans, quiz_results, job_skills)
- [ ] Enable pgvector extension in Supabase
- [ ] Load jobs dataset as embeddings into job_skills table
- [ ] Build Agent 1 (Skill Gap Analyzer) — RAG + DeepSeek + Structured Output
- [ ] Build Agent 2 (Learning Path Planner) — milestone generation
- [ ] Test full Agent 1 -> Agent 2 pipeline end-to-end in Python

### Phase 2 — The Core Loop
- [ ] Build Agent 3a (Morning Brief Generator) — cheat sheet JSON -> HTML email via Resend
- [ ] Build Agent 3b (Quiz Conductor) — MCQ generation + evaluation + conditional edge
- [ ] Test conditional edge: score >= 70 advances, score < 70 triggers replanner subgraph
- [ ] Wrap everything in FastAPI endpoints (/analyze, /plan, /quiz/{id}, /submit, /report)
- [ ] Deploy to Modal (modal deploy) — test web endpoint + cron triggers

### Phase 3 — Frontend
- [ ] Scaffold SvelteKit project with Tailwind
- [ ] Build landing page (SSR)
- [ ] Build onboarding form — calls FastAPI /analyze and /plan (NO AUTH NEEDED YET)
- [ ] Build dashboard — reads milestones from Supabase (use a hardcoded test user_id)
- [ ] Build /quiz page (client-only) — renders MCQs, submits answers to FastAPI
- [ ] Build /results page — shows score + feedback
- [ ] Build LinkedIn post card in dashboard — displays AI-generated post with "Copy & Post" button
- [ ] Deploy to Vercel (connect GitHub, auto-deploy)
- [ ] [OPTIONAL — add last] Set up Supabase Auth + Google OAuth in SvelteKit
  - Auth is a drop-in layer: add hooks.server.js + redirect guards AFTER core loop is working
  - Develop and test everything with a hardcoded user_id — auth does not block any other work

### Phase 4 — Polish + Evidence
- [ ] Add LangSmith tracing to all agent nodes
- [ ] Run full loop: onboard -> plan -> morning email -> quiz -> fail -> plan updates -> quiz -> pass
- [ ] Take LangSmith trace screenshots for PPT
- [ ] Record demo video of complete loop
- [ ] Design Resend email templates (morning brief + quiz link + results)
- [ ] Build Agent 4 (Progress Report + LinkedIn post)

---

## API Security Checklist (Amit Tiwari's Rules)

- [ ] DEEPSEEK_API_KEY in Modal secrets (modal secret create)
- [ ] GEMINI_API_KEY in Modal secrets (embedding generation only — used during dataset setup)
- [ ] SUPABASE_URL and SUPABASE_SERVICE_KEY in Modal secrets
- [ ] RESEND_API_KEY in Modal secrets
- [ ] LANGSMITH_API_KEY in Modal secrets
- [ ] SUPABASE_ANON_KEY in Vercel environment variables (public, safe)
- [ ] VITE_API_URL in Vercel pointing to Modal web endpoint URL
- [ ] No secrets committed to GitHub (.env in .gitignore)
- [ ] Supabase RLS policies enabled — users can only read their own data

---

## Stack Card

```
+----------------------------------------------------------+
|  STACK CARD: SkillBridge                                 |
+----------------------------------------------------------+
|  Approach:         Core Loop, Executed Perfectly         |
|  Frontend:         SvelteKit + Tailwind (Hybrid SSR)     |
|  Backend:          FastAPI on Modal (web endpoint)       |
|  Scheduling:       Modal cron (7:30am + 4pm IST)         |
|  Database:         Supabase (PostgreSQL + pgvector)      |
|  Auth:             Supabase Auth + Google OAuth          |
|  LLM:              DeepSeek V4 Flash (langchain-deepseek)|
|  Embeddings:       gemini-embedding-001 (Google AI free) |
|  Email:            Resend (HTML templates)               |
|  RAG:              pgvector (inside Supabase)            |
|  Tracing:          LangSmith                             |
|  Infra:            Vercel (FE) + Modal (BE + cron)       |
|  Payments:         N/A                                   |
|  Cost:             ~$0/mo (Modal $30 free credits)       |
|  Complexity:       Medium-High                           |
|  Time to MVP:      2-3 weeks                             |
|  Best first spike: Agent 3b conditional edge (replan)    |
|  Key risk:         DeepSeek API confirmed working India  |
|  LinkedIn:         AI-generated post + Copy & Post btn   |
|  Auth:             Toggleable layer — build last         |
|  Resume headline:  "Self-correcting multi-agent system   |
|                     on Modal with daily cron delivery"   |
+----------------------------------------------------------+
```

---

## The One-Line Pitch

> "ChatGPT tells you what to learn. SkillBridge sends you a cheat sheet at breakfast, tests you after school, and automatically rewrites your roadmap when you fail. It does not give advice — it takes action, every single day."

---

## Submission Checklist (Deadline: 20th July 2026)

- [ ] IBM SkillsBuild certificate uploaded to dashboard
- [ ] Lean Canvas exported as PDF -> submitted via "Submit Concept Note"
- [ ] Project PPT -> submitted via "Final Deliverable"
- [ ] PPT includes: live Vercel URL + LangSmith trace screenshots + demo video link
- [ ] LangSmith traces showing Agent 3b conditional edge (the self-correction proof)
