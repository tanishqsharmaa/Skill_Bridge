from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.learning_planner.schemas import MilestoneList
from src.agents.state import SkillBridgeState
from src.core.llm_client import get_llm
from src.db.client import get_supabase

_PROMPT_PATH = (
    Path(__file__).parent.parent.parent / "prompts" / "learning_planner.md"
)


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def plan_milestones(state: SkillBridgeState) -> SkillBridgeState:
    """Node 1: take SkillGapReport → DeepSeek → MilestoneList → INSERT learning_plans."""
    report = state["skill_gap_report"]
    hours = state.get("hours_per_week", 10)

    # Summarise skills needing work (non-zero gap, sorted by priority)
    skills_to_learn = sorted(
        [s for s in report["skills"] if s["gap_score"] > 0],
        key=lambda s: s["priority"],
    )
    skills_summary = "\n".join(
        f"- {s['name']}: gap={s['gap_score']}, priority={s['priority']}"
        for s in skills_to_learn
    )

    llm = get_llm(temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=MilestoneList)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _load_prompt()),
        (
            "human",
            "Target weeks: {total_weeks}\n"
            "Hours per week: {hours}\n"
            "Skills to cover (ordered by priority):\n{skills_summary}\n\n"
            "{format_instructions}",
        ),
    ])

    chain = prompt | llm | parser

    milestone_list: MilestoneList = chain.invoke({
        "total_weeks": report["recommended_timeline_weeks"],
        "hours": hours,
        "skills_summary": skills_summary,
        "format_instructions": parser.get_format_instructions(),
    })

    # Persist to learning_plans
    supabase = get_supabase()
    supabase.table("learning_plans").insert({
        "user_id": state["user_id"],
        "milestones": [m.model_dump() for m in milestone_list.milestones],
        "current_milestone_index": 0,
        "is_active": True,
        "plan_revision_count": 0,
    }).execute()

    log_entry = (
        f"plan_milestones: {milestone_list.total_weeks} weeks, "
        f"{len(milestone_list.milestones)} milestones for user={state['user_id']}"
    )

    return {
        **state,
        "learning_plan": [m.model_dump() for m in milestone_list.milestones],
        "current_milestone_index": 0,
        "plan_revision_count": 0,
        "progress_log": state.get("progress_log", []) + [log_entry],
    }
