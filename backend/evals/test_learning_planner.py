"""Gated evals for Agent 2 — Learning Path Planner.

These tests make real LLM calls and cost API quota.
Only run when the environment variable RUN_EVALS=1 is set.

Usage:
    RUN_EVALS=1 python -m pytest evals/test_learning_planner.py -v
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_EVALS") != "1",
    reason="Set RUN_EVALS=1 to run learning planner evals",
)

# Fixture: a realistic SkillGapReport for a backend dev goal
FIXTURE_STATE = {
    "user_id": "00000000-0000-0000-0000-000000000099",
    "user_goal": "Get a backend developer job at an Indian startup",
    "current_skills": ["Python", "SQL"],
    "hours_per_week": 10,
    "progress_log": [],
    "skill_gap_report": {
        "skills": [
            {"name": "FastAPI", "required_level": 8, "current_level": 2, "gap_score": 6, "priority": 1},
            {"name": "Docker", "required_level": 6, "current_level": 1, "gap_score": 5, "priority": 2},
            {"name": "PostgreSQL", "required_level": 7, "current_level": 3, "gap_score": 4, "priority": 3},
        ],
        "overall_readiness_percent": 35,
        "recommended_timeline_weeks": 4,
    },
}

PAID_PLATFORMS = ("udemy.com", "linkedin.com", "pluralsight.com", "skillshare.com")
ALLOWED_DOMAINS = ("youtube.com", "github.com", "coursera.org")


def test_milestone_schema_valid():
    """Agent 2 with a real LLM call must return a valid MilestoneList."""
    from unittest.mock import patch, MagicMock
    from src.agents.learning_planner.schemas import MilestoneList

    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    with patch("src.agents.learning_planner.nodes.get_supabase", return_value=mock_sb):
        from src.agents.learning_planner.graph import learning_planner_graph
        result = learning_planner_graph.invoke(FIXTURE_STATE)

    assert "learning_plan" in result
    assert isinstance(result["learning_plan"], list)
    assert len(result["learning_plan"]) >= 1
    # Re-validate all milestones through schema
    for m_dict in result["learning_plan"]:
        from src.agents.learning_planner.schemas import Milestone
        Milestone(**m_dict)  # raises if invalid


def test_resources_are_free():
    """Agent 2 must not produce any paid platform URLs in free_resources."""
    from unittest.mock import patch, MagicMock

    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    with patch("src.agents.learning_planner.nodes.get_supabase", return_value=mock_sb):
        from src.agents.learning_planner.graph import learning_planner_graph
        result = learning_planner_graph.invoke(FIXTURE_STATE)

    for milestone in result["learning_plan"]:
        for url in milestone["free_resources"]:
            for paid in PAID_PLATFORMS:
                assert paid not in url, f"Found paid resource: {url}"


def test_weeks_align_with_hours():
    """For hours_per_week=5 and recommended_timeline_weeks=4, output must have >= 2 weeks."""
    from unittest.mock import patch, MagicMock

    light_state = {**FIXTURE_STATE, "hours_per_week": 5}
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    with patch("src.agents.learning_planner.nodes.get_supabase", return_value=mock_sb):
        from src.agents.learning_planner.graph import learning_planner_graph
        result = learning_planner_graph.invoke(light_state)

    assert len(result["learning_plan"]) >= 2, (
        f"Expected >= 2 milestones for 4-week plan, got {len(result['learning_plan'])}"
    )
