"""Agent quality evals for Agent 1 — Skill Gap Analyzer.

These tests call the REAL graph (no mocks). They are skipped by default
to avoid burning API quota in CI. Set RUN_EVALS=1 to run them.

Run:
    $env:RUN_EVALS="1"
    pytest evals/test_skill_gap.py -v
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_EVALS") != "1",
    reason="Set RUN_EVALS=1 to run agent quality evals (uses real API calls)",
)

# Reuse same test user as integration test (fixture manages lifecycle)
EVAL_USER_ID = "00000000-0000-0000-0000-000000000099"

FIXTURE_STATE = {
    "user_id": EVAL_USER_ID,
    "user_goal": "Get a data analyst job at a product startup in India",
    "current_skills": ["Excel", "SQL", "Python basics"],
    "hours_per_week": 15,
    "progress_log": [],
}


@pytest.fixture(autouse=True)
def clean_skill_gaps():
    """Clean up any skill_gaps rows for the eval user before and after."""
    from src.db.client import get_supabase
    sb = get_supabase()
    sb.table("skill_gaps").delete().eq("user_id", EVAL_USER_ID).execute()
    sb.table("profiles").upsert({
        "id": EVAL_USER_ID,
        "email": "eval@skillbridge.test",
        "goal": "Data analyst",
    }).execute()
    yield
    sb.table("skill_gaps").delete().eq("user_id", EVAL_USER_ID).execute()
    sb.table("profiles").delete().eq("id", EVAL_USER_ID).execute()


def test_schema_valid():
    """Agent 1 output must parse as a valid SkillGapReport without errors."""
    from src.agents.skill_gap.graph import skill_gap_graph
    from src.agents.skill_gap.schemas import SkillGapReport

    result = skill_gap_graph.invoke(FIXTURE_STATE)
    report = SkillGapReport(**result["skill_gap_report"])  # raises on invalid schema
    assert report is not None


def test_readiness_in_range():
    """overall_readiness_percent must be in [0, 100]."""
    from src.agents.skill_gap.graph import skill_gap_graph

    result = skill_gap_graph.invoke(FIXTURE_STATE)
    pct = result["skill_gap_report"]["overall_readiness_percent"]
    assert 0 <= pct <= 100, f"Readiness out of range: {pct}"


def test_no_invented_skills():
    """All returned skill names must appear in the RAG context (no hallucination)."""
    from src.agents.skill_gap.graph import skill_gap_graph
    from src.retrieval.embeddings import embed_query
    from src.retrieval.vector_store import search_job_skills

    result = skill_gap_graph.invoke(FIXTURE_STATE)
    rag_rows = search_job_skills(embed_query(FIXTURE_STATE["user_goal"]), limit=20)
    rag_skills_lower = {r["skill"].lower() for r in rag_rows}

    invented = [
        entry["name"]
        for entry in result["skill_gap_report"]["skills"]
        if entry["name"].lower() not in rag_skills_lower
    ]
    assert not invented, f"Hallucinated skills (not in RAG context): {invented}"


def test_priority_ordering():
    """Skills must be ordered by gap_score descending when sorted by priority."""
    from src.agents.skill_gap.graph import skill_gap_graph

    result = skill_gap_graph.invoke(FIXTURE_STATE)
    skills = result["skill_gap_report"]["skills"]
    # Sort by priority ascending → gap_scores should be descending
    sorted_by_priority = sorted(skills, key=lambda x: x["priority"])
    gap_scores = [s["gap_score"] for s in sorted_by_priority]
    assert gap_scores == sorted(gap_scores, reverse=True), (
        f"Skills not sorted by gap_score desc: {gap_scores}"
    )
