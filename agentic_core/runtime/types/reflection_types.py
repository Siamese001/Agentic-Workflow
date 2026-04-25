"""Shared reflection types — used by both L3 task-reflexion and L1 retrieval-reflexion.

Per the W4.2 binding spec at ``docs/reports/plans/reflexion-retriever-binding.md``,
the L3 ``reflexion_engine`` (task outcomes) and the L1 ``retrieval_reflexion``
loop (chunk relevance) share **only** the dataclass shape and verdict/action
enums declared here. Each layer instantiates the dataclass with its own type
bound for ``evidence_in``:

* L3: ``evidence_in = TaskOutcome``
* L1: ``evidence_in = list[GradeVerdict]`` (per ADR-060 §2)

This module sits at ``agentic_core/runtime/types/`` — a dependency floor for
both L1 and L3. Importing from here from L3 → L1 is forbidden by the layer-
gravity gate; importing from this module is allowed from any layer.

Determinism: a reflection's ``next_action`` decision MUST be reproducible from
``(evidence_in, verdict, grader_identity)`` plus the tier in which it ran.
``ReflectionTrace`` records exactly those inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ReflectionVerdict(Enum):
    """Tri-state outcome of a single reflection step."""

    ACCEPT = "accept"
    """Evidence is sufficient; downstream may proceed without revision."""

    REVISE = "revise"
    """Evidence is partial or ambiguous; expand or rewrite and try again."""

    ABORT = "abort"
    """Evidence is unrecoverable; signal abstain to the caller."""


class ReflectionNextAction(Enum):
    """The next concrete step a reflection emits.

    L1 retrieval scope vs. L3 orchestration scope is enforced by the executor,
    not by this enum — both layers share the values but use different subsets.
    """

    # L1 retrieval scope
    REWRITE_QUERY = "rewrite_query"
    GRAPH_HOP = "graph_hop"
    TRANSFORM_SWAP = "transform_swap"

    # L3 orchestration scope
    REPLAN = "replan"
    RETRY_TOOL = "retry_tool"

    # Both scopes
    ABSTAIN = "abstain"
    ACCEPT_AS_IS = "accept_as_is"


L1_RETRIEVAL_ACTIONS: frozenset[ReflectionNextAction] = frozenset(
    {
        ReflectionNextAction.REWRITE_QUERY,
        ReflectionNextAction.GRAPH_HOP,
        ReflectionNextAction.TRANSFORM_SWAP,
        ReflectionNextAction.ABSTAIN,
        ReflectionNextAction.ACCEPT_AS_IS,
    }
)
"""Actions allowed inside an L1 retrieval reflexion loop.

Per W4.2 §3, L1 may not emit ``REPLAN`` or ``RETRY_TOOL`` — those signal
upward to L3 instead of being executed locally.
"""


L3_ORCHESTRATION_ACTIONS: frozenset[ReflectionNextAction] = frozenset(
    {
        ReflectionNextAction.REPLAN,
        ReflectionNextAction.RETRY_TOOL,
        ReflectionNextAction.ABSTAIN,
        ReflectionNextAction.ACCEPT_AS_IS,
    }
)
"""Actions allowed inside the existing L3 task-reflexion engine."""


@dataclass(frozen=True)
class ReflectionTrace:
    """One reflection step, with full reproducibility inputs captured.

    ``evidence_in`` is typed as ``Any`` because the two consumers have
    different domain types (TaskOutcome at L3, list[GradeVerdict] at L1).
    Each layer asserts the concrete type at construction time.

    ``rationale`` is bounded to keep traces compact and grep-friendly; longer
    explanations belong in OTel span events, not in the trace record.
    """

    iteration: int
    evidence_in: Any
    verdict: ReflectionVerdict
    rationale: str
    next_action: ReflectionNextAction | None
    grader_identity: str
    emitted_at: datetime
    extras: dict[str, Any] = field(default_factory=dict)
    """Free-form per-layer telemetry that doesn't merit a typed field.

    Examples:
    - L1: ``{"verdict_dist": {"relevant": 3, "ambiguous": 2, ...}}``
    - L3: ``{"task_id": "...", "attempt": 2}``
    """

    def __post_init__(self) -> None:
        if self.iteration < 0:
            raise ValueError(f"iteration must be >= 0, got {self.iteration}")
        if not isinstance(self.verdict, ReflectionVerdict):
            raise TypeError(f"verdict must be ReflectionVerdict, got {type(self.verdict).__name__}")
        if self.next_action is not None and not isinstance(self.next_action, ReflectionNextAction):
            raise TypeError(
                f"next_action must be ReflectionNextAction or None, got {type(self.next_action).__name__}"
            )
        # Bound rationale to keep records compact (W4.2 §6 determinism).
        if len(self.rationale) > 240:
            raise ValueError(f"rationale must be <= 240 chars, got {len(self.rationale)}")


__all__ = [
    "ReflectionVerdict",
    "ReflectionNextAction",
    "ReflectionTrace",
    "L1_RETRIEVAL_ACTIONS",
    "L3_ORCHESTRATION_ACTIONS",
]
