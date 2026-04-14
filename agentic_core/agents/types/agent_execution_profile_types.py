"""Agent Execution Profile Types - Single Source of Truth.

Defines the 2×2 execution policy for agent classification and enforcement.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ReasoningIntensity(str, Enum):
    """Agent reasoning intensity classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ExecutionMode(str, Enum):
    """Agent execution mode classification."""

    DETERMINISTIC = "DETERMINISTIC"
    LLM_API = "LLM_API"


def _normalize_allowed_models(allowed_models: tuple[str, ...]) -> tuple[str, ...]:
    """Return deduplicated model names with whitespace removed."""
    normalized: list[str] = []
    for model in allowed_models:
        if not isinstance(model, str):
            raise TypeError("allowed_models entries must be strings")
        cleaned = model.strip()
        if not cleaned:
            raise ValueError("allowed_models entries must be non-empty strings")
        if cleaned not in normalized:
            normalized.append(cleaned)
    return tuple(normalized)


def _to_canonical_data(value: Any) -> Any:
    """Convert nested registry data into a JSON-stable structure."""
    if isinstance(value, AgentExecutionProfile):
        return value.to_dict()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {
            str(key): _to_canonical_data(val)
            for key, val in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_to_canonical_data(item) for item in value]
    return value


@dataclass(frozen=True)
class AgentExecutionProfile:
    """Immutable agent execution profile defining the 2×2 execution policy."""

    agent_id: str
    reasoning_intensity: ReasoningIntensity
    execution_mode: ExecutionMode
    allowed_models: tuple[str, ...]
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate profile constraints and normalize stable fields."""
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")

        object.__setattr__(self, "agent_id", self.agent_id.strip())
        object.__setattr__(self, "allowed_models", _normalize_allowed_models(tuple(self.allowed_models)))

        if self.notes is not None and not isinstance(self.notes, str):
            raise TypeError("notes must be a string or None")

        if self.execution_mode == ExecutionMode.DETERMINISTIC and self.allowed_models:
            raise ValueError(f"Deterministic agent {self.agent_id} cannot have allowed_models")
        if self.execution_mode == ExecutionMode.LLM_API and not self.allowed_models:
            raise ValueError(f"LLM_API agent {self.agent_id} must have allowed_models")

    def is_llm_allowed(self) -> bool:
        """Check if agent is allowed to use an LLM API."""
        return self.execution_mode == ExecutionMode.LLM_API

    def can_use_model(self, model: str) -> bool:
        """Check if agent can use a specific model."""
        return isinstance(model, str) and model.strip() in self.allowed_models

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "reasoning_intensity": self.reasoning_intensity.value,
            "execution_mode": self.execution_mode.value,
            "allowed_models": list(self.allowed_models),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentExecutionProfile":
        """Create a profile from a JSON-deserialized dictionary."""
        required_keys = {"agent_id", "reasoning_intensity", "execution_mode", "allowed_models"}
        missing_keys = sorted(required_keys.difference(data))
        if missing_keys:
            raise KeyError(f"Missing required profile keys: {missing_keys}")

        allowed_models = data["allowed_models"]
        if not isinstance(allowed_models, (list, tuple)):
            raise TypeError("allowed_models must be a list or tuple")

        return cls(
            agent_id=data["agent_id"],
            reasoning_intensity=ReasoningIntensity(data["reasoning_intensity"]),
            execution_mode=ExecutionMode(data["execution_mode"]),
            allowed_models=tuple(allowed_models),
            notes=data.get("notes"),
        )


def compute_registry_digest(registry_data: dict[str, Any]) -> str:
    """Compute SHA256 digest over canonical JSON of sorted registry data."""
    canonical_json = json.dumps(
        _to_canonical_data(registry_data),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


__all__ = [
    "AgentExecutionProfile",
    "ExecutionMode",
    "ReasoningIntensity",
    "compute_registry_digest",
]
