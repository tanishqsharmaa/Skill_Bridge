from pydantic import BaseModel, Field, model_validator


class SkillEntry(BaseModel):
    """A single skill with gap analysis fields.

    gap_score is validated to always equal required_level - current_level,
    so the LLM cannot produce inconsistent data.
    """

    name: str = Field(..., description="Skill name — must come from the RAG context")
    required_level: int = Field(..., ge=1, le=10)
    current_level: int = Field(..., ge=0, le=10)
    gap_score: int = Field(..., ge=0, le=10)
    priority: int = Field(..., ge=1, description="1 = highest priority gap to close")

    @model_validator(mode="after")
    def gap_score_is_consistent(self) -> "SkillEntry":
        expected = max(0, self.required_level - self.current_level)
        if self.gap_score != expected:
            raise ValueError(
                f"gap_score must equal required_level - current_level "
                f"(expected {expected}, got {self.gap_score})"
            )
        return self


class SkillGapReport(BaseModel):
    """Full output of Agent 1 — persisted to skill_gaps table."""

    skills: list[SkillEntry] = Field(..., min_length=1)
    overall_readiness_percent: int = Field(..., ge=0, le=100)
    recommended_timeline_weeks: int = Field(..., ge=1)
