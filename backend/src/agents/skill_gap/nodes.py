from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.skill_gap.schemas import SkillGapReport
from src.agents.state import SkillBridgeState
from src.core.llm_client import get_llm
from src.db.client import get_supabase
from src.retrieval.embeddings import embed_query
from src.retrieval.vector_store import search_job_skills

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "skill_gap_analyzer.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def analyze_gaps(state: SkillBridgeState) -> SkillBridgeState:
    """Node 1: embed user goal → RAG retrieval → DeepSeek → SkillGapReport.

    Does NOT write to the DB — that happens in safety_net after the safety
    check, so the stored report already has the corrected timeline.
    """
    goal = state["user_goal"]
    skills = state["current_skills"]

    # 1. Embed goal and retrieve the 20 most relevant job-market skills
    query_vector = embed_query(goal)
    rag_rows = search_job_skills(query_vector, limit=20)
    rag_context = "\n".join(
        f"- {r['role']} | {r['skill']} | importance={r['importance_level']}"
        for r in rag_rows
    )

    # 2. Build chain: prompt | llm | PydanticOutputParser
    llm = get_llm(temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=SkillGapReport)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _load_prompt()),
        (
            "human",
            "User goal: {goal}\n"
            "Current skills: {skills}\n"
            "Job market context (top 20 skills by similarity):\n{rag_context}\n\n"
            "{format_instructions}",
        ),
    ])

    chain = prompt | llm | parser

    report: SkillGapReport = chain.invoke({
        "goal": goal,
        "skills": ", ".join(skills),
        "rag_context": rag_context,
        "format_instructions": parser.get_format_instructions(),
    })

    log_entry = (
        f"analyze_gaps: readiness={report.overall_readiness_percent}%, "
        f"skills={len(report.skills)}, weeks={report.recommended_timeline_weeks}"
    )

    return {
        **state,
        "skill_gap_report": report.model_dump(),
        "progress_log": state.get("progress_log", []) + [log_entry],
    }


def safety_net(state: SkillBridgeState) -> SkillBridgeState:
    """Node 2: apply safety cap then persist the final report to skill_gaps.

    If overall_readiness_percent < 20, forces recommended_timeline_weeks to 24
    (prevents the LLM from scheduling an impossibly short plan for beginners).
    The corrected report is then inserted into skill_gaps.
    """
    report_dict = dict(state["skill_gap_report"])
    log = list(state.get("progress_log", []))

    if report_dict["overall_readiness_percent"] < 20:
        report_dict["recommended_timeline_weeks"] = 24
        log.append("safety_net: readiness < 20% → forced timeline to 24 weeks")

    # Insert final (possibly corrected) report into Supabase
    supabase = get_supabase()
    supabase.table("skill_gaps").insert({
        "user_id": state["user_id"],
        "skill_gap_report": report_dict,
        "overall_readiness_percent": report_dict["overall_readiness_percent"],
    }).execute()

    log.append(
        f"safety_net: inserted skill_gaps row for user={state['user_id']}"
    )

    return {**state, "skill_gap_report": report_dict, "progress_log": log}
