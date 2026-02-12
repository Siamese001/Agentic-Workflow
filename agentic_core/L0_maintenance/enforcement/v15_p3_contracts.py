"""
V15 P3 Framework Contracts — Governance & Human Escalation Enforcement.

Runtime contracts enforcing P3 (Governance) invariants required by
the V15 Target State audit (Prompt v5.0 Enhanced).

Contract version: 1.0.0
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.L0_maintenance.types.v15_p3_types import (
    EvidencePack,
    ExceptionScope,
    PolicyExceptionArtifact,
    PolicySnapshot,
    PolicyUpdateProposal,
    RouteDecisionRef,
)

_log = logging.getLogger(__name__)

# =============================================================================
# §3.4 — build_evidence_pack
# =============================================================================


class EvidencePackError(Exception):
    """Raised when EvidencePack construction fails (fail-closed)."""


def build_evidence_pack(
    trace_id: str,
    action_trace: tuple[str, ...],
    policy_evals: tuple[str, ...],
    risk_score: float,
    budget_breach_data: dict[str, object],
    boundary_snapshot_hash: str,
) -> EvidencePack:
    """§3.4 — Build a structured EvidencePack for human escalation.

    Fail-closed: any invalid field raises EvidencePackError.
    """
    try:
        pack = EvidencePack(
            trace_id=trace_id,
            action_trace=action_trace,
            policy_evals=policy_evals,
            risk_score=risk_score,
            budget_breach_data=budget_breach_data,
            boundary_snapshot_hash=boundary_snapshot_hash,
        )
    except (ValueError, TypeError) as exc:
        raise EvidencePackError(
            f"FAIL (P3): EvidencePack construction failed: {exc}",
        ) from exc
    return pack


def validate_evidence_pack(pack: Any) -> EvidencePack:
    """§3.4 — Validate that an object is a well-formed EvidencePack."""
    if not isinstance(pack, EvidencePack):
        raise EvidencePackError(
            f"FAIL (P3): Expected EvidencePack, got {type(pack).__name__}",
        )
    return pack


def build_hil_evidence_pack(
    trace_id: str,
    escalation_reason: str,
    route_decision_ref: RouteDecisionRef,
    policy_snapshot_data: PolicySnapshot,
    risk_score: float = 0.8,
    action_trace: tuple[str, ...] = (),
    policy_evals: tuple[str, ...] = (),
    guardian_results: tuple[str, ...] = (),
    ssot_hash: str = "",
    attachments: tuple[str, ...] = (),
) -> EvidencePack:
    """§Wave2.2 — Build a full EvidencePack for HIL escalation.

    Fail-closed: any invalid field raises EvidencePackError.
    """
    try:
        pack = EvidencePack(
            trace_id=trace_id,
            action_trace=action_trace,
            policy_evals=policy_evals,
            risk_score=risk_score,
            budget_breach_data={},
            boundary_snapshot_hash=ssot_hash or "n/a",
            evidence_id=str(uuid.uuid4()),
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            escalation_reason=escalation_reason,
            route_decision_ref=route_decision_ref,
            guardian_results=guardian_results,
            policy_snapshot_data=policy_snapshot_data,
            ssot_hash=ssot_hash,
            attachments=attachments,
        )
    except (ValueError, TypeError) as exc:
        raise EvidencePackError(
            f"FAIL (P3/Wave2.2): HIL EvidencePack construction failed: {exc}",
        ) from exc
    return pack


# =============================================================================
# §3.7 — emit_policy_exception
# =============================================================================


class PolicyExceptionError(Exception):
    """Raised when PolicyExceptionArtifact construction or validation fails."""


def emit_policy_exception(
    trace_id: str,
    exception_scope: ExceptionScope,
    semantic_clock_tick: int,
    issuer_signature: str,
    nonce: str | None = None,
) -> PolicyExceptionArtifact:
    """§3.7 — Emit a PolicyExceptionArtifact for a policy challenge.

    Generates a cryptographic nonce if not provided.
    Fail-closed: any invalid field raises PolicyExceptionError.
    """
    if nonce is None:
        nonce = secrets.token_hex(16)

    try:
        artifact = PolicyExceptionArtifact(
            trace_id=trace_id,
            nonce=nonce,
            exception_scope=exception_scope,
            semantic_clock_tick=semantic_clock_tick,
            issuer_signature=issuer_signature,
        )
    except (ValueError, TypeError) as exc:
        raise PolicyExceptionError(
            f"FAIL (P3): PolicyExceptionArtifact construction failed: {exc}",
        ) from exc
    return artifact


def validate_policy_exception_tick(
    artifact: PolicyExceptionArtifact,
    current_tick: int,
) -> bool:
    """§3.7 — Validate that a policy exception is valid for the current tick.

    An exception is valid ONLY for the semantic clock tick it was issued at.
    Returns True if valid, raises PolicyExceptionError if expired.
    """
    if artifact.semantic_clock_tick != current_tick:
        raise PolicyExceptionError(
            f"FAIL (P3): PolicyException expired. "
            f"Issued at tick {artifact.semantic_clock_tick}, current tick {current_tick}.",
        )
    return True


# =============================================================================
# §3.5 — propose_policy_update
# =============================================================================


class PolicyUpdateError(Exception):
    """Raised when PolicyUpdateProposal construction or validation fails."""


def propose_policy_update(
    trace_id: str,
    override_id: str,
    proposed_policy_diff: str,
    originating_agent: str,
    semantic_clock_tick: int,
) -> PolicyUpdateProposal:
    """§3.5 — Emit a PolicyUpdateProposal for bidirectional feedback.

    Emitted when a human override occurs, proposing a policy change
    back to the Policy Update Mechanism.
    Fail-closed: any invalid field raises PolicyUpdateError.
    """
    try:
        proposal = PolicyUpdateProposal(
            trace_id=trace_id,
            override_id=override_id,
            proposed_policy_diff=proposed_policy_diff,
            originating_agent=originating_agent,
            semantic_clock_tick=semantic_clock_tick,
        )
    except (ValueError, TypeError) as exc:
        raise PolicyUpdateError(
            f"FAIL (P3): PolicyUpdateProposal construction failed: {exc}",
        ) from exc
    return proposal


def validate_proposal(proposal: Any) -> PolicyUpdateProposal:
    """§3.5 — Validate that an object is a well-formed PolicyUpdateProposal."""
    if not isinstance(proposal, PolicyUpdateProposal):
        raise PolicyUpdateError(
            f"FAIL (P3): Expected PolicyUpdateProposal, got {type(proposal).__name__}",
        )
    return proposal


__all__ = [
    "EvidencePackError",
    "PolicyExceptionError",
    "PolicyUpdateError",
    "build_evidence_pack",
    "build_hil_evidence_pack",
    "emit_policy_exception",
    "propose_policy_update",
    "validate_evidence_pack",
    "validate_policy_exception_tick",
    "validate_proposal",
]
