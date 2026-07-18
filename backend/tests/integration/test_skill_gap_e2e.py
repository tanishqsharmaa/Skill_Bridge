"""Integration test — runs skill_gap_graph against live Supabase.

Requires:
  - .env filled with real secrets
  - Supabase project live with job_skills seeded (≥100 rows)
  - DeepSeek API key active

Run:
    pytest tests/integration/test_skill_gap_e2e.py -v
"""
import pytest
from src.db.client import get_supabase

# Fixed UUID that is unlikely to collide with real users.
TEST_USER_ID = "00000000-0000-0000-0000-000000000099"

TEST_STATE = {
    "user_id": TEST_USER_ID,
    "user_goal": "Get a backend developer job at an Indian product startup",
    "current_skills": ["Python", "REST APIs", "SQL"],
    "hours_per_week": 10,
    "progress_log": [],
}


@pytest.fixture(autouse=True)
def manage_test_user():
    """Create a minimal profiles row before the test; clean up skill_gaps + profile after."""
    sb = get_supabase()
    # Upsert so re-runs don't fail on duplicate
    sb.table("profiles").upsert({
        "id": TEST_USER_ID,
        "email": "integration-test@skillbridge.test",
        "goal": "Backend dev",
    }).execute()

    yield  # test runs here

    # Always clean up — even if the test fails
    sb.table("skill_gaps").delete().eq("user_id", TEST_USER_ID).execute()
    sb.table("profiles").delete().eq("id", TEST_USER_ID).execute()


def test_full_agent1_pipeline():
    """End-to-end: graph invoke → skill_gaps row inserted with correct readiness_percent."""
    from src.agents.skill_gap.graph import skill_gap_graph

    result = skill_gap_graph.invoke(TEST_STATE)

    # Output shape
    assert "skill_gap_report" in result
    report = result["skill_gap_report"]
    assert 0 <= report["overall_readiness_percent"] <= 100
    assert report["recommended_timeline_weeks"] >= 1
    assert len(report["skills"]) >= 1

    # DB row was inserted
    sb = get_supabase()
    rows = sb.table("skill_gaps").select("*").eq("user_id", TEST_USER_ID).execute().data
    assert len(rows) == 1
    assert rows[0]["overall_readiness_percent"] == report["overall_readiness_percent"]


def test_progress_log_populated():
    """Graph must append at least 2 progress_log entries (one per node)."""
    from src.agents.skill_gap.graph import skill_gap_graph

    result = skill_gap_graph.invoke(TEST_STATE)
    assert len(result.get("progress_log", [])) >= 2
