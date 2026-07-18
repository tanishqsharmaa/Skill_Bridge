"""Unit tests for Agent 2 — Learning Path Planner nodes and schemas.

All external I/O (LLM, Supabase) is mocked — these tests run offline.
"""
import pytest
from unittest.mock import MagicMock, patch

from src.agents.learning_planner.schemas import Milestone, MilestoneList


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_milestone(week: int = 1, **overrides) -> Milestone:
    defaults = dict(
        week=week,
        topic="Python Basics",
        daily_subtopics=[
            "Install Python and set up a virtual environment",
            "Learn variables, data types, and basic I/O",
            "Practice control flow: if/elif/else and loops",
            "Write functions and understand scope",
            "Read files and handle exceptions",
        ],
        free_resources=["https://www.youtube.com/watch?v=python-basics"],
        milestone_id=f"python-basics-week-{week}",
    )
    defaults.update(overrides)
    return Milestone(**defaults)


def _make_milestone_list(n: int = 2) -> MilestoneList:
    milestones = [_make_milestone(week=i + 1) for i in range(n)]
    # Make milestone_ids unique across weeks
    for i, m in enumerate(milestones):
        object.__setattr__(m, "milestone_id", f"python-basics-week-{i + 1}")
    return MilestoneList(milestones=milestones, total_weeks=n)


BASE_STATE = {
    "user_id": "00000000-0000-0000-0000-000000000002",
    "user_goal": "Get a backend dev job at an Indian startup",
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


def _mock_supabase():
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    return mock_sb


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

def test_daily_subtopics_count_validator_rejects_wrong_count():
    """Milestone must raise ValidationError if daily_subtopics != 5 items."""
    with pytest.raises(Exception):
        Milestone(
            week=1,
            topic="Python",
            daily_subtopics=["Only three", "items here", "not five"],
            free_resources=["https://www.youtube.com/watch?v=abc"],
            milestone_id="python-week-1",
        )


def test_free_resources_validator_rejects_paid_domain():
    """Milestone must raise ValueError if a resource URL is from a paid platform."""
    with pytest.raises(ValueError, match="Resource URL must be from"):
        Milestone(
            week=1,
            topic="Python",
            daily_subtopics=[
                "Day 1", "Day 2", "Day 3", "Day 4", "Day 5"
            ],
            free_resources=["https://www.udemy.com/course/python"],
            milestone_id="python-week-1",
        )


def test_free_resources_validator_accepts_valid_domains():
    """Milestone must NOT raise for youtube.com, github.com, coursera.org URLs."""
    m = _make_milestone(
        free_resources=[
            "https://www.youtube.com/watch?v=abc",
            "https://github.com/some/repo",
            "https://www.coursera.org/learn/python",
        ]
    )
    assert len(m.free_resources) == 3


def test_total_weeks_validator_rejects_mismatch():
    """MilestoneList must raise if total_weeks != len(milestones)."""
    with pytest.raises(ValueError, match="total_weeks"):
        MilestoneList(
            milestones=[_make_milestone(week=1)],
            total_weeks=5,  # wrong — only 1 milestone
        )


def test_total_weeks_validator_passes_when_correct():
    """MilestoneList must not raise when total_weeks == len(milestones)."""
    ml = MilestoneList(
        milestones=[_make_milestone(week=1), _make_milestone(week=2)],
        total_weeks=2,
    )
    assert ml.total_weeks == 2


# ---------------------------------------------------------------------------
# plan_milestones node tests
# ---------------------------------------------------------------------------

def _setup_mock_chain(mock_pt, mock_get_llm, return_value):
    """Wire up the LangChain pipe operator mock so chain.invoke returns return_value."""
    prompt_mock = mock_pt.from_messages.return_value
    llm_mock = mock_get_llm.return_value
    step1 = prompt_mock | llm_mock
    chain = step1 | MagicMock()
    chain.invoke.return_value = return_value
    return chain


def test_plan_milestones_returns_learning_plan_in_state():
    """plan_milestones must return state with 'learning_plan' key containing milestone dicts."""
    mock_ml = _make_milestone_list(n=2)

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=_mock_supabase()):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        result = plan_milestones(BASE_STATE)

    assert "learning_plan" in result
    assert isinstance(result["learning_plan"], list)
    assert len(result["learning_plan"]) == 2


def test_plan_milestones_daily_subtopics_count():
    """Every milestone in the output must have exactly 5 daily subtopics."""
    mock_ml = _make_milestone_list(n=2)

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=_mock_supabase()):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        result = plan_milestones(BASE_STATE)

    for milestone in result["learning_plan"]:
        assert len(milestone["daily_subtopics"]) == 5


def test_plan_milestones_free_resources_valid_domains():
    """Every resource URL in the output must be from an allowed free domain."""
    mock_ml = _make_milestone_list(n=2)
    allowed = ("youtube.com", "github.com", "coursera.org")

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=_mock_supabase()):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        result = plan_milestones(BASE_STATE)

    for milestone in result["learning_plan"]:
        for url in milestone["free_resources"]:
            assert any(domain in url for domain in allowed), f"Disallowed URL: {url}"


def test_plan_milestones_milestone_ids_unique():
    """All milestone_id values in the output must be unique."""
    mock_ml = _make_milestone_list(n=2)

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=_mock_supabase()):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        result = plan_milestones(BASE_STATE)

    ids = [m["milestone_id"] for m in result["learning_plan"]]
    assert len(ids) == len(set(ids)), f"Duplicate milestone_ids found: {ids}"


def test_plan_milestones_inserts_supabase_row():
    """plan_milestones must call Supabase insert on learning_plans exactly once."""
    mock_ml = _make_milestone_list(n=2)
    mock_sb = _mock_supabase()

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=mock_sb):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        plan_milestones(BASE_STATE)

    mock_sb.table.assert_called_once_with("learning_plans")
    mock_sb.table.return_value.insert.assert_called_once()


def test_plan_milestones_sets_index_and_revision_to_zero():
    """plan_milestones must set current_milestone_index=0 and plan_revision_count=0."""
    mock_ml = _make_milestone_list(n=2)

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=_mock_supabase()):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        result = plan_milestones(BASE_STATE)

    assert result["current_milestone_index"] == 0
    assert result["plan_revision_count"] == 0


def test_plan_milestones_appends_to_progress_log():
    """plan_milestones must append exactly one entry to progress_log."""
    mock_ml = _make_milestone_list(n=2)

    with patch("src.agents.learning_planner.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.learning_planner.nodes.PydanticOutputParser"), \
         patch("src.agents.learning_planner.nodes.get_llm") as mock_get_llm, \
         patch("src.agents.learning_planner.nodes.get_supabase", return_value=_mock_supabase()):

        _setup_mock_chain(mock_pt, mock_get_llm, mock_ml)

        from src.agents.learning_planner.nodes import plan_milestones
        result = plan_milestones({**BASE_STATE, "progress_log": ["existing_entry"]})

    assert len(result["progress_log"]) == 2
    assert "plan_milestones" in result["progress_log"][-1]
