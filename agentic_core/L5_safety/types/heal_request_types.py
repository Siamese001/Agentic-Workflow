"""HealRequest — typed heal request with snapshot binding (B06 — GAP-006, REQ-010).

The heal loop MUST bind to the same policy_hash/blueprint_hash as the originating
execution.  Upgrading to a newer policy mid-run breaks determinism and makes the
repair non-replayable.

Layer authority: L5_safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,
    _emit_links_execution_to_snapshot,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "heal_request_types")
emit_determinism_digest("p0", "heal_request_types")
_emit_reads_policy_state("p1", "heal_request_types", "L5")
_emit_verifies_policy("p1", "heal_request_types", "heal_policy_check")
_emit_verifies_boundary("p1", "heal_request_types", "heal_boundary_check")
_emit_dispatches_healing_run("p1", "heal_request_types", "heal_dispatch")
_emit_links_execution_to_snapshot("p1", "heal_request_types", "snapshot_link")


class SnapshotMismatchError(RuntimeError):
    """Raised when the heal loop attempts to use a different snapshot than the originating run.

    The heal loop must always bind to the same policy_hash and blueprint_hash
    as the execution it is repairing.  Any divergence breaks determinism.
    """


@dataclass(frozen=True)
class HealRequest:
    """Typed heal request with mandatory snapshot binding (REQ-010).

    Fields:
        request_id         — unique identifier for this heal request
        parent_packet_id   — packet_id of the originating execution being healed
        policy_hash        — hash of the policy snapshot from the originating execution
        blueprint_hash     — hash of the blueprint snapshot from the originating execution
        violation_payload  — dict describing the violation to be healed
        originating_run_id — run_id of the execution this heal request belongs to
    """

    request_id: str
    parent_packet_id: str
    policy_hash: str
    blueprint_hash: str
    violation_payload: dict
    originating_run_id: str

    def validate(self) -> None:
        """Raise ValueError if any mandatory field is missing."""
        missing = []
        for f in (
            "request_id",
            "parent_packet_id",
            "policy_hash",
            "blueprint_hash",
            "originating_run_id",
        ):
            val = getattr(self, f, None)
            if not val or not str(val).strip():
                missing.append(f)
        if missing:
            raise ValueError(
                f"HealRequest is missing mandatory fields: {missing}. "
                "All heal loop paths must provide full snapshot binding."
            )
        if not isinstance(self.violation_payload, dict):
            raise ValueError(
                f"HealRequest.violation_payload must be a dict, got {type(self.violation_payload).__name__}."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "parent_packet_id": self.parent_packet_id,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "violation_payload": self.violation_payload,
            "originating_run_id": self.originating_run_id,
        }


def assert_same_snapshot(
    heal_request: HealRequest,
    originating_policy_hash: str,
    originating_blueprint_hash: str,
) -> None:
    """Assert that heal_request uses the same snapshot as the originating execution.

    Called by HealingStrategy before any repair action.

    Raises:
        SnapshotMismatchError: if policy_hash or blueprint_hash diverge.
    """
    _emit_records_execution_trace("heal_snapshot_check", "heal_request_types", heal_request.request_id)
    if heal_request.policy_hash != originating_policy_hash:
        raise SnapshotMismatchError(
            f"HealRequest policy_hash mismatch: heal={heal_request.policy_hash!r} "
            f"vs originating={originating_policy_hash!r}. "
            "Heal loop must bind to the same policy snapshot as the originating execution."
        )
    if heal_request.blueprint_hash != originating_blueprint_hash:
        raise SnapshotMismatchError(
            f"HealRequest blueprint_hash mismatch: heal={heal_request.blueprint_hash!r} "
            f"vs originating={originating_blueprint_hash!r}. "
            "Heal loop must bind to the same blueprint snapshot as the originating execution."
        )


# =============================================================================
# W2 additive: HealResult return contract (plan c8e4f1)
# =============================================================================
# Per `docs/reference/04_L2_Execute/04_L2_Execute_v2.md` §E3/§E4/§E5, heal()
# MUST return a typed result classifying the outcome into one of four
# terminal classes plus the metadata needed to seal the E5 artifact.


class HealOutcome(str, Enum):
    """Tri-class + escalation outcome per L2 Execute v2 §E3 classification.

    Values are the literal strings emitted in the E5 sealed artifact.
    """

    SUCCESS = "SUCCESS"
    SOFT_REPAIRABLE = "SOFT_REPAIRABLE"
    FAIL_TERMINAL = "FAIL_TERMINAL"
    NEEDS_HELP = "NEEDS_HELP"


@dataclass(frozen=True, slots=True)
class HealResult:
    """Typed return contract for every E4 Fixing Desk heal() invocation.

    Fields map 1:1 to the E5 seal schema. All heal implementations MUST return
    a HealResult; stub dicts and NotImplementedError both violate the contract.

    Fields:
        outcome            - HealOutcome classification (SUCCESS/SOFT_REPAIRABLE/FAIL_TERMINAL/NEEDS_HELP)
        reason_code        - short machine-readable code (e.g. "schema_mismatch", "max_retries_exhausted")
        parent_packet_id   - the originating E2 packet being repaired (links E2 -> E4 -> E5)
        repair_count       - attempt counter; MUST be <= MAX_REPAIR_COUNT from SovereignHealerBase
        policy_hash        - policy snapshot from the originating packet (MUST match parent)
        blueprint_hash     - blueprint snapshot from the originating packet (MUST match parent)
        evidence           - structured repair evidence (diffs, before/after, tool outputs)
        message            - optional human-readable summary
    """

    outcome: HealOutcome
    reason_code: str
    parent_packet_id: str
    repair_count: int
    policy_hash: str
    blueprint_hash: str
    evidence: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, HealOutcome):
            # Allow callers to pass the raw string; normalize or raise.
            try:
                object.__setattr__(self, "outcome", HealOutcome(str(self.outcome)))
            except ValueError as exc:
                raise ValueError(
                    f"HealResult.outcome must be a HealOutcome or one of "
                    f"{[o.value for o in HealOutcome]}; got {self.outcome!r}"
                ) from exc
        if not self.reason_code or not self.reason_code.strip():
            raise ValueError("HealResult.reason_code is required (non-empty)")
        if not self.parent_packet_id or not self.parent_packet_id.strip():
            raise ValueError("HealResult.parent_packet_id is required (non-empty)")
        if not isinstance(self.repair_count, int) or self.repair_count < 0:
            raise ValueError(
                f"HealResult.repair_count must be int >= 0; got {self.repair_count!r}"
            )
        if not self.policy_hash or not self.blueprint_hash:
            raise ValueError(
                "HealResult requires non-empty policy_hash and blueprint_hash "
                "per L2 Execute v2 §E4 snapshot-binding invariant"
            )
        if not isinstance(self.evidence, dict):
            raise ValueError(
                f"HealResult.evidence must be dict; got {type(self.evidence).__name__}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "reason_code": self.reason_code,
            "parent_packet_id": self.parent_packet_id,
            "repair_count": self.repair_count,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "evidence": dict(self.evidence),
            "message": self.message,
        }

    @classmethod
    def from_request(
        cls,
        heal_request: "HealRequest",
        outcome: HealOutcome | str,
        reason_code: str,
        repair_count: int = 1,
        evidence: Optional[dict[str, Any]] = None,
        message: str = "",
    ) -> "HealResult":
        """Factory: build a HealResult inheriting snapshot binding from a HealRequest.

        Preferred construction path — guarantees policy_hash/blueprint_hash
        match the originating packet per §E4 invariant.
        """
        return cls(
            outcome=outcome if isinstance(outcome, HealOutcome) else HealOutcome(str(outcome)),
            reason_code=reason_code,
            parent_packet_id=heal_request.parent_packet_id,
            repair_count=repair_count,
            policy_hash=heal_request.policy_hash,
            blueprint_hash=heal_request.blueprint_hash,
            evidence=evidence or {},
            message=message,
        )

    @classmethod
    def needs_help(
        cls,
        parent_packet_id: str,
        policy_hash: str,
        blueprint_hash: str,
        reason_code: str = "not_implemented",
        message: str = "",
    ) -> "HealResult":
        """Shortcut for heal() implementations that must escalate instead of repair.

        Used by W3 to replace the 4 stub heal() implementations that currently
        raise NotImplementedError or return {"status": "skipped"}.
        """
        return cls(
            outcome=HealOutcome.NEEDS_HELP,
            reason_code=reason_code,
            parent_packet_id=parent_packet_id or "unknown",
            repair_count=0,
            policy_hash=policy_hash or "unknown",
            blueprint_hash=blueprint_hash or "unknown",
            evidence={},
            message=message,
        )
