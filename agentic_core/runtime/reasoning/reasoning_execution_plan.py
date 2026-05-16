"""Immutable reasoning execution plan (pre-call contract surface)."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.reasoning.reasoning_control_requirement import ReasoningControlRequirement


@dataclass(frozen=True, slots=True)
class ReasoningExecutionPlan:
    """Structured intent forwarded to resolver + provider.

    ``requested_values`` uses stable control_name keys (temperature, cot_paths, ...).
    """

    plan_digest: str
    control_requirements: tuple[ReasoningControlRequirement, ...]
    requested_values: dict[str, float | int | str | bool | None]


__all__ = ["ReasoningExecutionPlan"]
