from pydantic import BaseModel, Field, model_validator


class Milestone(BaseModel):
    """A single weekly learning milestone."""

    week: int = Field(..., ge=1)
    topic: str = Field(..., description="Main topic for the week")
    daily_subtopics: list[str] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="Exactly 5 subtopics — one per day Mon-Fri",
    )
    free_resources: list[str] = Field(
        ...,
        min_length=1,
        description="Only youtube.com, github.com, or coursera.org URLs",
    )
    milestone_id: str = Field(
        ..., description="Slugified topic, e.g. 'python-basics-week-1'"
    )

    @model_validator(mode="after")
    def resources_are_free_domains(self) -> "Milestone":
        allowed = ("youtube.com", "github.com", "coursera.org")
        for url in self.free_resources:
            if not any(domain in url for domain in allowed):
                raise ValueError(
                    f"Resource URL must be from youtube.com, github.com, or "
                    f"coursera.org. Got: {url}"
                )
        return self


class MilestoneList(BaseModel):
    """Full output of Agent 2 — persisted to learning_plans table."""

    milestones: list[Milestone] = Field(..., min_length=1)
    total_weeks: int = Field(..., ge=1)

    @model_validator(mode="after")
    def total_weeks_matches_milestones(self) -> "MilestoneList":
        if self.total_weeks != len(self.milestones):
            raise ValueError(
                f"total_weeks ({self.total_weeks}) must equal "
                f"len(milestones) ({len(self.milestones)})"
            )
        return self
