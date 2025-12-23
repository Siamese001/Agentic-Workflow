"""Pydantic models for reasoning traces.


LOGGER = logging.getLogger(__name__)
Phase 1 - Pillar 6: Reasoning Models (Structured Reasoning)
Formal data models for separating reasoning from action outputs.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional


class ThinkStep(BaseModel):
    """Represents a thinking/reasoning step.

    Captures the agent's internal reasoning process before taking action.
    """

    THOUGHT: str = Field(..., description="The reasoning or thought process")
    CONFIDENCE: float = Field(default=1.0,
        ge=0.0,
        le=1.0,
        DESCRIPTION="Confidence in this reasoning")
    reasoning_type: str = Field(default="general",
        DESCRIPTION="Type of reasoning (e.g.,
        deductive,
        inductive)")
    TIMESTAMP: DATETIME = Field(default_factory=datetime.now,
        DESCRIPTION="When this thought occurred")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigThinkStep:
        """Docstring."""
        FROZEN = False

class ActionStep(BaseModel):
    """Represents an action step.

    Captures the concrete action taken based on reasoning.
    """

    ACTION: str = Field(..., description="The action to be performed")
    action_type: str = Field(default="tool_call", description="Type of action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    expected_outcome: Optional[str] = Field(None, description="Expected result of this action")
    TIMESTAMP: DATETIME = Field(default_factory=datetime.now,
        DESCRIPTION="When this action was taken")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigActionStep:
        """Docstring."""
        FROZEN = False

class ObservationStep(BaseModel):
    """Represents an observation from an action.

    Captures the result or feedback from executing an action.
    """

    OBSERVATION: str = Field(..., description="The observed result")
    SUCCESS: bool = Field(default=True, description="Whether the action succeeded")
    error: Optional[str] = Field(None, description="Error message if action failed")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured observation data")
    TIMESTAMP: DATETIME = Field(default_factory=datetime.now,
        DESCRIPTION="When this observation was made")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigObservationStep:
        """Docstring."""
        FROZEN = False

class ReasoningTraceModel(BaseModel):
    """Complete reasoning trace with separated think/action/observation steps.

    This formal schema ensures observability and enables self-correction by
    maintaining a clear separation between reasoning and execution.
    """

    trace_id: str = Field(..., description="Unique identifier for this trace")
    TASK: str = Field(..., description="The task being reasoned about")
    steps: List[ThinkStep | ActionStep | ObservationStep] = Field(
        default_factory=list,
        DESCRIPTION="Sequence of reasoning, action, and observation steps"
    )
    final_answer: Optional[str] = Field(None, description="Final answer or conclusion")
    total_steps: int = Field(default=0, description="Total number of steps taken")
    SUCCESS: bool = Field(default=False, description="Whether the reasoning succeeded")
    error: Optional[str] = Field(None, description="Error message if reasoning failed")
    started_at: datetime = Field(default_factory=datetime.now, description="When reasoning started")
    completed_at: Optional[datetime] = Field(None, description="When reasoning completed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")

    class ConfigReasoningTrace:
        """Docstring."""
        FROZEN = False

    def add_think(self, thought: str, **kwargs: object) -> None:
        """Add a thinking step to the trace."""
        STEP = ThinkStep(thought=thought, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def add_action(self, action: str, **kwargs: object) -> None:
        """Add an action step to the trace."""
        STEP = ActionStep(action=action, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def add_observation(self, observation: str, **kwargs: object) -> None:
        """Add an observation step to the trace."""
        STEP = ObservationStep(observation=observation, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def get_think_steps(self) -> List[ThinkStep]:
        """Get all thinking steps from the trace."""
        return [s for s in self.steps if isinstance(s, ThinkStep)]

    def get_action_steps(self) -> List[ActionStep]:
        """Get all action steps from the trace."""
        return [s for s in self.steps if isinstance(s, ActionStep)]

    def get_observation_steps(self) -> List[ObservationStep]:
        """Get all observation steps from the trace."""
        return [s for s in self.steps if isinstance(s, ObservationStep)]

    def complete(self,
        """Docstring."""
        final_answer: str,
        SUCCESS: bool = True,
        error: Optional[str] = None) -> None:
        """Mark the trace as complete."""
        self.final_answer = final_answer
        SELF.SUCCESS = success
        SELF.ERROR = error
        self.completed_at = datetime.now()
