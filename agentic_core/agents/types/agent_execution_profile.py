"""Agent Execution Profile Types - Single Source of Truth

Defines the 2×2 execution policy for agent classification and enforcement.
"""

import hashlib
import json
from dataclasses import dataclass
from enum import Enum


class ReasoningIntensity(Enum):
    """Agent reasoning intensity classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"  # Added for apps_* agents
    HIGH = "HIGH"


class ExecutionMode(Enum):
    """Agent execution mode classification."""
    DETERMINISTIC = "DETERMINISTIC"
    LLM_API = "LLM_API"


@dataclass(frozen=True)
class AgentExecutionProfile:
    """Immutable agent execution profile defining 2×2 policy."""
    agent_id: str  # stable key
    reasoning_intensity: ReasoningIntensity
    execution_mode: ExecutionMode
    allowed_models: tuple[str, ...]  # empty for deterministic agents
    notes: str | None = None  # non-functional documentation

    def __post_init__(self):
        """Validate profile constraints."""
        # Deterministic agents must have no allowed models
        if self.execution_mode == ExecutionMode.DETERMINISTIC and self.allowed_models:
            raise ValueError(f"Deterministic agent {self.agent_id} cannot have allowed_models")

        # LLM_API agents must have at least one allowed model
        if self.execution_mode == ExecutionMode.LLM_API and not self.allowed_models:
            raise ValueError(f"LLM_API agent {self.agent_id} must have allowed_models")

        # Agent ID must be stable (non-empty string)
        if not self.agent_id or not isinstance(self.agent_id, str):
            raise ValueError("agent_id must be a non-empty string")

    def is_llm_allowed(self) -> bool:
        """Check if agent is allowed to use LLM API."""
        return self.execution_mode == ExecutionMode.LLM_API

    def can_use_model(self, model: str) -> bool:
        """Check if agent can use specific model."""
        return model in self.allowed_models

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "reasoning_intensity": self.reasoning_intensity.value,
            "execution_mode": self.execution_mode.value,
            "allowed_models": list(self.allowed_models),
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentExecutionProfile":
        """Create from dictionary for JSON deserialization."""
        return cls(
            agent_id=data["agent_id"],
            reasoning_intensity=ReasoningIntensity(data["reasoning_intensity"]),
            execution_mode=ExecutionMode(data["execution_mode"]),
            allowed_models=tuple(data["allowed_models"]),
            notes=data.get("notes")
        )


def compute_registry_digest(registry_data: dict) -> str:
    """Compute SHA256 digest over canonical JSON of sorted registry."""
    # Canonical JSON: sorted keys, compact separators, ASCII
    canonical_json = json.dumps(
        registry_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True
    )
    return hashlib.sha256(canonical_json.encode()).hexdigest()


if __name__ == "__main__":
    # Example usage and validation
    example_profile = AgentExecutionProfile(
        agent_id="example_agent",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "gpt-3.5-turbo"),
        notes="Example high-reasoning LLM agent"
    )

    print(f"Profile: {example_profile}")
    print(f"Is LLM allowed: {example_profile.is_llm_allowed()}")
    print(f"Can use gpt-4: {example_profile.can_use_model('gpt-4')}")
    print(f"Dict representation: {example_profile.to_dict()}")
