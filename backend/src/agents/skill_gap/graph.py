from langgraph.graph import StateGraph, END

from src.agents.skill_gap.nodes import analyze_gaps, safety_net
from src.agents.state import SkillBridgeState

_builder = StateGraph(SkillBridgeState)
_builder.add_node("analyze_gaps", analyze_gaps)
_builder.add_node("safety_net", safety_net)
_builder.set_entry_point("analyze_gaps")
_builder.add_edge("analyze_gaps", "safety_net")
_builder.add_edge("safety_net", END)

# Public export — Sprint 6 FastAPI router imports this directly.
skill_gap_graph = _builder.compile()
