"""Unit tests for Agent 1 nodes and schemas.

All external I/O (LLM, Supabase, Gemini) is mocked — these tests run offline.
"""
import pytest
from unittest.mock import MagicMock, patch

from src.agents.skill_gap.schemas import SkillEntry, SkillGapReport


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_report(**overrides) -> SkillGapReport:
    defaults = dict(
        skills=[
            SkillEntry(name="Python", required_level=8, current_level=5, gap_score=3, priority=1),
            SkillEntry(name="FastAPI", required_level=7, current_level=2, gap_score=5, priority=2),
        ],
        overall_readiness_percent=55,
        recommended_timeline_weeks=8,
    )
    defaults.update(overrides)
    return SkillGapReport(**defaults)


BASE_STATE = {
    "user_id": "00000000-0000-0000-0000-000000000001",
    "user_goal": "Get a backend dev job at an Indian startup",
    "current_skills": ["Python", "SQL"],
    "hours_per_week": 10,
    "progress_log": [],
}


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

def test_gap_score_validator_catches_mismatch():
    """SkillEntry must raise ValueError if gap_score != required - current."""
    with pytest.raises(ValueError, match="gap_score must equal"):
        SkillEntry(
            name="Python", required_level=8, current_level=5,
            gap_score=9,  # wrong — should be 3
            priority=1,
        )


def test_gap_score_validator_passes_when_correct():
    """SkillEntry must not raise when gap_score == required - current."""
    entry = SkillEntry(
        name="Python", required_level=8, current_level=5, gap_score=3, priority=1
    )
    assert entry.gap_score == 3


def test_gap_score_floored_at_zero():
    """gap_score == 0 when current_level >= required_level is valid."""
    entry = SkillEntry(
        name="Python", required_level=5, current_level=8, gap_score=0, priority=1
    )
    assert entry.gap_score == 0


# ---------------------------------------------------------------------------
# analyze_gaps node tests
# ---------------------------------------------------------------------------

@patch("src.agents.skill_gap.nodes.search_job_skills", return_value=[
    {"role": "Backend Dev", "skill": "Python", "importance_level": 5},
    {"role": "Backend Dev", "skill": "FastAPI", "importance_level": 4},
])
@patch("src.agents.skill_gap.nodes.embed_query", return_value=[0.1] * 768)
def test_analyze_gaps_returns_schema(mock_embed, mock_search):
    """analyze_gaps must return state with skill_gap_report matching SkillGapReport schema."""
    mock_report = _make_report()

    with patch("src.agents.skill_gap.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.skill_gap.nodes.PydanticOutputParser"), \
         patch("src.agents.skill_gap.nodes.get_llm") as mock_get_llm:

        # MagicMock.__or__ is deterministic: mock_a | anything always returns
        # mock_a.__or__.return_value (same object regardless of right operand).
        # Pre-compute what `chain = prompt | llm | parser` will resolve to, so
        # we can set chain.invoke.return_value before analyze_gaps runs.
        prompt_mock = mock_pt.from_messages.return_value
        llm_mock = mock_get_llm.return_value
        step1 = prompt_mock | llm_mock        # prompt_mock.__or__.return_value
        chain = step1 | MagicMock()           # step1.__or__.return_value (same as step1 | parser)
        chain.invoke.return_value = mock_report

        from src.agents.skill_gap.nodes import analyze_gaps
        result = analyze_gaps(BASE_STATE)

    assert "skill_gap_report" in result
    # Re-validate through schema to confirm the dict shape is correct
    SkillGapReport(**result["skill_gap_report"])



@patch("src.agents.skill_gap.nodes.search_job_skills", return_value=[
    {"role": "Backend Dev", "skill": "Python", "importance_level": 5},
])
@patch("src.agents.skill_gap.nodes.embed_query", return_value=[0.1] * 768)
def test_analyze_gaps_appends_to_progress_log(mock_embed, mock_search):
    """analyze_gaps must append exactly one entry to progress_log."""
    mock_report = _make_report()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_report

    with patch("src.agents.skill_gap.nodes.ChatPromptTemplate") as mock_pt, \
         patch("src.agents.skill_gap.nodes.PydanticOutputParser"), \
         patch("src.agents.skill_gap.nodes.get_llm"):
        mock_pt.from_messages.return_value.__or__ = lambda self, other: mock_chain
        from src.agents.skill_gap.nodes import analyze_gaps
        result = analyze_gaps({**BASE_STATE, "progress_log": ["existing"]})

    assert len(result["progress_log"]) == 2
    assert "analyze_gaps" in result["progress_log"][-1]


# ---------------------------------------------------------------------------
# safety_net node tests
# ---------------------------------------------------------------------------

def _mock_supabase():
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    return mock_sb


def test_safety_net_forces_24_weeks_when_readiness_below_20():
    """safety_net must set recommended_timeline_weeks=24 when readiness < 20."""
    state = {
        **BASE_STATE,
        "skill_gap_report": _make_report(
            overall_readiness_percent=15,
            recommended_timeline_weeks=40,
        ).model_dump(),
    }
    with patch("src.agents.skill_gap.nodes.get_supabase", return_value=_mock_supabase()):
        from src.agents.skill_gap.nodes import safety_net
        result = safety_net(state)

    assert result["skill_gap_report"]["recommended_timeline_weeks"] == 24
    assert any("24 weeks" in entry for entry in result["progress_log"])


def test_safety_net_noop_when_readiness_at_exactly_20():
    """safety_net must NOT alter the timeline when readiness == 20 (boundary)."""
    state = {
        **BASE_STATE,
        "skill_gap_report": _make_report(
            overall_readiness_percent=20,
            recommended_timeline_weeks=12,
        ).model_dump(),
    }
    with patch("src.agents.skill_gap.nodes.get_supabase", return_value=_mock_supabase()):
        from src.agents.skill_gap.nodes import safety_net
        result = safety_net(state)

    assert result["skill_gap_report"]["recommended_timeline_weeks"] == 12


def test_safety_net_noop_above_20():
    """safety_net must NOT alter the timeline when readiness > 20."""
    state = {
        **BASE_STATE,
        "skill_gap_report": _make_report(
            overall_readiness_percent=55,
            recommended_timeline_weeks=8,
        ).model_dump(),
    }
    with patch("src.agents.skill_gap.nodes.get_supabase", return_value=_mock_supabase()):
        from src.agents.skill_gap.nodes import safety_net
        result = safety_net(state)

    assert result["skill_gap_report"]["recommended_timeline_weeks"] == 8


def test_safety_net_calls_supabase_insert():
    """safety_net must always call Supabase insert regardless of readiness."""
    state = {
        **BASE_STATE,
        "skill_gap_report": _make_report(overall_readiness_percent=55).model_dump(),
    }
    mock_sb = _mock_supabase()
    with patch("src.agents.skill_gap.nodes.get_supabase", return_value=mock_sb):
        from src.agents.skill_gap.nodes import safety_net
        safety_net(state)

    mock_sb.table.assert_called_once_with("skill_gaps")
    mock_sb.table.return_value.insert.assert_called_once()
