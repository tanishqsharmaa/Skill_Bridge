from langgraph.graph import StateGraph, END

from src.agents.learning_planner.nodes import plan_milestones
from src.agents.state import SkillBridgeState

_builder = StateGraph(SkillBridgeState)
_builder.add_node("plan_milestones", plan_milestones)
_builder.set_entry_point("plan_milestones")
_builder.add_edge("plan_milestones", END)

# Public export — Sprint 6 FastAPI router imports this directly.
learning_planner_graph = _builder.compile()
