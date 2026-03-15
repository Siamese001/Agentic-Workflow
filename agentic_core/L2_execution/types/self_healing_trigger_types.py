"""
§Wave4.3 — L2SelfHealingTrigger: authorized, deterministic healing trigger.

Emitted from the control spine ONLY when healing is authorized:
  (a) L5 auto-approves healing for the request/risk tier, OR
  (b) HIL approves healing escalation

NOT emitted from L1 or L6. NOT emitted when rejected/pending/read-only.

Deterministic contract:
  - SemanticClockSnapshot required (Phase 3.2)
  - recommended_actions sorted
  - trace_id is SHA-256 of canonical payload (no uuid4)
  - No wall-clock timestamps, no elapsed_ms
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "self_healing_trigger_types")
_emit_applies_guardrail("p0", "self_healing_trigger_types", "p0_governance")
_emit_snapshots_state("p0", "self_healing_trigger_types", "state_snapshot")

# =============================================================================
# §Wave4.3 — Authorization decision enum (string, not Enum object)
# =============================================================================

AUTHORIZED_DECISIONS: frozenset[str] = frozenset(
    {
        "AUTO_APPROVED",
        "HIL_APPROVED",
    },
)

REJECTED_DECISIONS: frozenset[str] = frozenset(
    {
        "REJECTED",
        "PENDING",
        "READ_ONLY",
        "NOT_APPROVED",
    },
)


# =============================================================================
# §Wave4.3 — L2SelfHealingTrigger
# =============================================================================


@dataclass(frozen=True)
class L2SelfHealingTrigger:
    """§Wave4.3 — Authorized self-healing trigger emitted at L2 control spine.

    Required fields:
      artifact_type        — fixed "SELF_HEALING_TRIGGER"
      semantic_clock       — required SemanticClockSnapshot
      trace_id             — deterministic (SHA-256 of canonical payload)
      target               — stable identifier (file path or subsystem key)
      reason_code          — stable string (no Enum objects)
      recommended_actions  — sorted tuple of action strings
      risk_tier            — tier string (e.g., "low", "medium", "high", "critical")
      authorization        — how healing was authorized ("AUTO_APPROVED" or "HIL_APPROVED")
      policy_config_hash   — optional
      route_context        — optional stable string
    """

    artifact_type: str
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    target: str
    reason_code: str
    recommended_actions: tuple[str, ...]
    risk_tier: str
    authorization: str
    policy_config_hash: str = ""
    route_context: str = ""

    def __post_init__(self) -> None:
        if self.artifact_type != "SELF_HEALING_TRIGGER":
            raise ValueError(
                f"L2SelfHealingTrigger: artifact_type must be 'SELF_HEALING_TRIGGER', "
                f"got '{self.artifact_type}'",
            )
        validate_semantic_clock(self.semantic_clock)
        if not self.trace_id:
            raise ValueError("L2SelfHealingTrigger: trace_id must be non-empty")
        if not self.target:
            raise ValueError("L2SelfHealingTrigger: target must be non-empty")
        if not self.reason_code:
            raise ValueError("L2SelfHealingTrigger: reason_code must be non-empty")
        if not isinstance(self.recommended_actions, tuple):
            raise TypeError(
                "L2SelfHealingTrigger: recommended_actions must be a tuple",
            )
        if list(self.recommended_actions) != sorted(self.recommended_actions):
            raise ValueError(
                "L2SelfHealingTrigger: recommended_actions must be sorted",
            )
        if not self.risk_tier:
            raise ValueError("L2SelfHealingTrigger: risk_tier must be non-empty")
        if self.authorization not in AUTHORIZED_DECISIONS:
            raise ValueError(
                f"L2SelfHealingTrigger: authorization must be one of "
                f"{sorted(AUTHORIZED_DECISIONS)}, got '{self.authorization}'",
            )

    def to_dict(self) -> dict[str, Any]:
        """Deterministic serialization with sorted keys."""
        return {
            "artifact_type": self.artifact_type,
            "authorization": self.authorization,
            "policy_config_hash": self.policy_config_hash,
            "reason_code": self.reason_code,
            "recommended_actions": list(self.recommended_actions),
            "risk_tier": self.risk_tier,
            "route_context": self.route_context,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target": self.target,
            "trace_id": self.trace_id,
        }


# =============================================================================
# §Wave4.3 — Authorization gate + emit factory
# =============================================================================


def _compute_trigger_trace_id(
    target: str,
    reason_code: str,
    actions: tuple[str, ...],
    tick: int,
) -> str:
    """Deterministic trace_id from canonical payload hash."""
    canonical = json.dumps(
        {
            "actions": list(actions),
            "reason_code": reason_code,
            "target": target,
            "tick": tick,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def is_healing_authorized(decision: str) -> bool:
    """§Wave4.3 — Check if a decision authorizes healing emission."""
    return decision in AUTHORIZED_DECISIONS


def emit_self_healing_trigger(
    decision: str,
    target: str,
    reason_code: str,
    recommended_actions: list[str],
    risk_tier: str,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str = "",
    route_context: str = "",
) -> L2SelfHealingTrigger | None:
    """§Wave4.3 — Emit a SelfHealingTrigger ONLY when authorized.

    Returns None if healing is not authorized (rejected/pending/read-only).
    Raises ValueError if semantic_clock is None (even for authorized paths).

    Authorization gate:
      AUTO_APPROVED / HIL_APPROVED → emit trigger
      Everything else → return None (no emission)
    """
    if not is_healing_authorized(decision):
        return None

    validate_semantic_clock(semantic_clock)

    normalized_actions = tuple(sorted(set(recommended_actions)))
    trace_id = _compute_trigger_trace_id(
        target,
        reason_code,
        normalized_actions,
        semantic_clock.tick,
    )

    return L2SelfHealingTrigger(
        artifact_type="SELF_HEALING_TRIGGER",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        target=target,
        reason_code=reason_code,
        recommended_actions=normalized_actions,
        risk_tier=risk_tier,
        authorization=decision,
        policy_config_hash=policy_config_hash,
        route_context=route_context,
    )


__all__ = [
    "AUTHORIZED_DECISIONS",
    "L2SelfHealingTrigger",
    "REJECTED_DECISIONS",
    "emit_self_healing_trigger",
    "is_healing_authorized",
]
