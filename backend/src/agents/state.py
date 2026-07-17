from typing import TypedDict


class SkillBridgeState(TypedDict, total=False):
    """Shared state passed between all LangGraph agent nodes.

    Uses total=False so every field is optional — nodes only populate the keys
    they produce, and downstream nodes read only the keys they need.
    """

    # ── User context (set once during onboarding) ──────────────────────────
    user_id: str               # UUID from Supabase profiles.id
    user_email: str            # For Resend delivery
    user_goal: str             # e.g. "Get a backend dev job at a product startup"
    current_skills: list[str]  # Self-assessed skills from onboarding form
    hours_per_week: int        # Available study hours (used by Agent 2)

    # ── Agent 1 output ─────────────────────────────────────────────────────
    skill_gap_report: dict     # Serialised SkillGapReport (see skill_gap/schemas.py)

    # ── Agent 2 output ─────────────────────────────────────────────────────
    learning_plan: list[dict]      # list[Milestone] (see learning_planner/schemas.py)
    current_milestone_index: int   # Pointer into learning_plan; incremented on pass
    plan_revision_count: int       # How many times the replanner has rewritten the plan

    # ── Agent 3a working state (Morning Brief) ─────────────────────────────
    morning_brief: dict        # Serialised MorningBrief (see daily_checkin/schemas.py)

    # ── Agent 3b working state (Quiz) ──────────────────────────────────────
    quiz_questions: list[dict] # list[QuizQuestion]
    quiz_id: str               # Unique key: {user_id_prefix}_{date}_{slug}
    quiz_answers: list[int]    # Student's selected option indices (0-indexed)
    quiz_result: dict          # Serialised QuizResult

    # ── Agent 4 output (Weekly Report) ─────────────────────────────────────
    weekly_report: dict        # Serialised WeeklyReport

    # ── Shared audit trail ─────────────────────────────────────────────────
    progress_log: list[str]    # Append-only log of agent actions for debugging
