from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class FramingProfile:
    global_goal: str
    success_criteria: str
    task_mode: str
    scope_boundaries: str
    cost_latency: Dict[str, Any]


DEFAULT_FRAMING_PROFILE = FramingProfile(
    global_goal="solve the user objective deterministically",
    success_criteria="correct, concise, aligned to instructions",
    task_mode="analytical",
    scope_boundaries="stay within provided state and allowed tools",
    cost_latency={"max_ms": 2000, "max_cost": 0.05},
)


@dataclass
class ContextProfile:
    untrusted_block_wrapping: bool
    canonicalize_inputs: bool
    apply_pruning_rules: bool
    enforce_structured_ordering: bool


DEFAULT_CONTEXT_PROFILE = ContextProfile(
    untrusted_block_wrapping=True,
    canonicalize_inputs=True,
    apply_pruning_rules=True,
    enforce_structured_ordering=True,
)
