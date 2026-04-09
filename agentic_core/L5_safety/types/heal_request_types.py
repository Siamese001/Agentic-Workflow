"""HealRequest — typed heal request with snapshot binding (B06 — GAP-006, REQ-010).

The heal loop MUST bind to the same policy_hash/blueprint_hash as the originating
execution.  Upgrading to a newer policy mid-run breaks determinism and makes the
repair non-replayable.

Layer authority: L5_safety.
"""

from __future__ import annotations

from dataclasses import dataclass
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
