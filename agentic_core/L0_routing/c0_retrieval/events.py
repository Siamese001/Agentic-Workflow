"""C0 observability event types — emitted at every stage transition.

Defense-in-depth: events MUST NOT carry retrieved text or credentials.
Mirrors intake/events.py forbidden-field guard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class C0Event(str, Enum):
    """Stage-transition events for L6 observability."""

    PREFLIGHT_EVALUATED = "C0PreflightEvaluated"
    PREFLIGHT_BLOCKED = "C0PreflightBlocked"
    RETRIEVAL_PLAN_BUILT = "C0RetrievalPlanBuilt"
    EVIDENCE_FETCHED = "C0EvidenceFetched"
    EVIDENCE_HYDRATED = "C0EvidenceHydrated"
    GRAPH_TRAVERSED = "C0GraphTraversed"
    EVIDENCE_SHAPED = "C0EvidenceShaped"
    CONFLICTS_DETECTED = "C0ConflictsDetected"
    EVIDENCE_SCORED = "C0EvidenceScored"
    GATE_FIRED = "C0GateFired"
    REFINE_ATTEMPTED = "C0RefineAttempted"
    CONTRACT_EMITTED = "C0ContractEmitted"
    CONTRACT_REJECTED = "C0ContractRejected"


# Fields that MUST NEVER appear in event payload.
FORBIDDEN_EVENT_FIELDS: frozenset[str] = frozenset(
    {
        "evidence_text",
        "raw_text",
        "user_task_text",
        "credential",
        "auth_token",
        "api_key",
        "password",
        "secret",
        "answer",
        "answer_text",
        "model_response",
    }
)


C0_METRIC_NAMES: tuple[str, ...] = (
    "c0_retrieval_count",
    "c0_preflight_block_rate",
    "c0_pass_rate",
    "c0_weak_rate",
    "c0_conflicted_rate",
    "c0_empty_rate",
    "c0_blocked_rate",
    "c0_refine_attempt_rate",
    "c0_refine_pass_rate",
    "c0_avg_support_score",
    "c0_avg_retrieval_latency_ms",
    "c0_acl_block_count",
    "c0_injection_quarantine_count",
    "c0_graph_hop_avg",
    "c0_token_estimate_avg",
)


@dataclass(frozen=True)
class C0EventRecord:
    """Single event in the observability stream."""

    event: C0Event
    contract_id: str
    route_id: str
    fields: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.event, C0Event):
            raise TypeError("event must be C0Event")
        for forbidden in FORBIDDEN_EVENT_FIELDS:
            if forbidden in self.fields:
                raise ValueError(
                    f"Event {self.event.value} cannot carry forbidden field {forbidden!r} "
                    "(C0.I2: retrieved text is data, never instruction; events leak nothing)"
                )
