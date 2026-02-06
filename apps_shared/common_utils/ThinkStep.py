"""Pydantic models for reasoning traces.

Phase 1 - Pillar 6: Reasoning models (Structured Reasoning)
Formal data models for separating reasoning from action outputs.
"""

from datetime import datetime


class ThinkStep(BaseModel):
    """Represents a thinking/reasoning step.

    Captures the agent's internal reasoning process before taking action.
    """

    thought: str = Field(..., description="The reasoning or thought process")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in this reasoning",
    )
    reasoning_type: str = Field(
        default="general", description="Type of reasoning (e.g., deductive, inductive)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When this thought occurred",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigThinkStep:
        frozen = False


class ActionStep(BaseModel):
    """Represents an action step.

    Captures the concrete action taken based on reasoning.
    """

    action: str = Field(..., description="The action to be performed")
    action_type: str = Field(default="tool_call", description="Type of action")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    expected_outcome: str | None = Field(None, description="Expected result of this action")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When this action was taken",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigActionStep:
        frozen = False


class ObservationStep(BaseModel):
    """Represents an observation from an action.

    Captures the result or feedback from executing an action.
    """

    observation: str = Field(..., description="The observed result")
    success: bool = Field(default=True, description="Whether the action succeeded")
    error: str | None = Field(None, description="Error message if action failed")
    data: dict[str, Any] = Field(default_factory=dict, description="Structured observation data")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When this observation was made",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigObservationStep:
        frozen = False


class ReasoningTraceModel(BaseModel):
    """Complete reasoning trace with separated think/action/observation steps.

    This formal schema ensures observability and enables self-correction by
    maintaining a clear separation between reasoning and execution.
    """

    trace_id: str = Field(..., description="Unique identifier for this trace")
    task: str = Field(..., description="The task being reasoned about")
    steps: list[ThinkStep | ActionStep | ObservationStep] = Field(
        default_factory=list, description="Sequence of reasoning, action, and observation steps",
    )
    final_answer: str | None = Field(None, description="Final answer or conclusion")
    total_steps: int = Field(default=0, description="Total number of steps taken")
    success: bool = Field(default=False, description="Whether the reasoning succeeded")
    error: str | None = Field(None, description="Error message if reasoning failed")
    started_at: datetime = Field(default_factory=datetime.now, description="When reasoning started")
    completed_at: datetime | None = Field(None, description="When reasoning completed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")

    class ConfigReasoningTrace:
        frozen = False

    def add_think(self, thought: str, **kwargs: object) -> None:
        """Add a thinking step to the trace."""
        step = ThinkStep(thought=thought, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def add_action(self, action: str, **kwargs: object) -> None:
        """Add an action step to the trace."""
        step = ActionStep(action=action, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def add_observation(self, observation: str, **kwargs: object) -> None:
        """Add an observation step to the trace."""
        step = ObservationStep(observation=observation, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def get_think_steps(self) -> list[ThinkStep]:
        """Get all thinking steps from the trace."""
        return [s for s in self.steps if isinstance(s, ThinkStep)]

    def get_action_steps(self) -> list[ActionStep]:
        """Get all action steps from the trace."""
        return [s for s in self.steps if isinstance(s, ActionStep)]

    def get_observation_steps(self) -> list[ObservationStep]:
        """Get all observation steps from the trace."""
        return [s for s in self.steps if isinstance(s, ObservationStep)]

    def complete(self, final_answer: str, success: bool = True, error: str | None = None) -> None:
        """Mark the trace as complete."""
        self.final_answer = final_answer
        self.success = success
        self.error = error
        self.completed_at = datetime.now()
