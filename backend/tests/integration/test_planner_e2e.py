"""Integration tests for Agent 2 — Learning Path Planner.

These tests make real Supabase and LLM calls.
They clean up after themselves — inserted rows are deleted post-test.

Run from Build/backend/ with venv activated:
    python -m pytest tests/integration/test_planner_e2e.py -v
"""
import pytest

TEST_USER_ID = "00000000-0000-0000-0000-000000000002"

# Minimal SkillGapReport that mimics Agent 1 output
FIXTURE_STATE = {
    "user_id": TEST_USER_ID,
    "user_goal": "Get a backend developer job at an Indian startup",
    "current_skills": ["Python", "SQL"],
    "hours_per_week": 10,
    "progress_log": [],
    "skill_gap_report": {
        "skills": [
            {"name": "FastAPI", "required_level": 8, "current_level": 2, "gap_score": 6, "priority": 1},
            {"name": "Docker", "required_level": 6, "current_level": 1, "gap_score": 5, "priority": 2},
        ],
        "overall_readiness_percent": 30,
        "recommended_timeline_weeks": 2,
    },
}


def _cleanup(supabase):
    """Delete all learning_plans rows created by integration tests."""
    supabase.table("learning_plans").delete().eq("user_id", TEST_USER_ID).execute()


def test_agent2_inserts_learning_plans_row():
    """Agent 2 must insert exactly one row into learning_plans for the test user."""
    from src.agents.learning_planner.graph import learning_planner_graph
    from src.db.client import get_supabase

    supabase = get_supabase()
    _cleanup(supabase)  # start clean

    try:
        result = learning_planner_graph.invoke(FIXTURE_STATE)

        # Verify state output
        assert "learning_plan" in result
        assert isinstance(result["learning_plan"], list)
        assert len(result["learning_plan"]) >= 1
        assert result["current_milestone_index"] == 0
        assert result["plan_revision_count"] == 0

        # Verify DB row
        rows = (
            supabase.table("learning_plans")
            .select("id, milestones, is_active, current_milestone_index")
            .eq("user_id", TEST_USER_ID)
            .execute()
            .data
        )
        assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
        assert rows[0]["is_active"] is True
        assert rows[0]["current_milestone_index"] == 0
        assert isinstance(rows[0]["milestones"], list)
        assert len(rows[0]["milestones"]) >= 1

    finally:
        _cleanup(supabase)


def test_agent1_into_agent2_pipeline():
    """Full chain: run Agent 1 then feed its output directly into Agent 2."""
    from src.agents.skill_gap.graph import skill_gap_graph
    from src.agents.learning_planner.graph import learning_planner_graph
    from src.db.client import get_supabase

    supabase = get_supabase()
    # Clean up both tables
    supabase.table("skill_gaps").delete().eq("user_id", TEST_USER_ID).execute()
    _cleanup(supabase)

    try:
        # Step 1: Agent 1
        initial_state = {
            "user_id": TEST_USER_ID,
            "user_goal": "Get a backend developer job at an Indian startup",
            "current_skills": ["Python", "SQL"],
            "hours_per_week": 10,
            "progress_log": [],
        }
        state_after_agent1 = skill_gap_graph.invoke(initial_state)
        assert "skill_gap_report" in state_after_agent1

        # Step 2: Agent 2 receives Agent 1 state
        state_after_agent2 = learning_planner_graph.invoke(state_after_agent1)

        assert "learning_plan" in state_after_agent2
        assert len(state_after_agent2["learning_plan"]) >= 1

        # Verify DB row from Agent 2
        rows = (
            supabase.table("learning_plans")
            .select("id, milestones, is_active")
            .eq("user_id", TEST_USER_ID)
            .execute()
            .data
        )
        assert len(rows) == 1, f"Expected 1 learning_plans row, got {len(rows)}"
        assert rows[0]["is_active"] is True

    finally:
        supabase.table("skill_gaps").delete().eq("user_id", TEST_USER_ID).execute()
        _cleanup(supabase)


def test_only_one_active_plan_per_user():
    """Calling Agent 2 twice for the same user must raise on the second call (unique constraint)."""
    from src.agents.learning_planner.graph import learning_planner_graph
    from src.db.client import get_supabase

    supabase = get_supabase()
    _cleanup(supabase)

    try:
        # First call — must succeed
        learning_planner_graph.invoke(FIXTURE_STATE)

        # Second call — must raise due to partial unique index on (user_id, is_active=True)
        with pytest.raises(Exception):
            learning_planner_graph.invoke(FIXTURE_STATE)

    finally:
        _cleanup(supabase)
