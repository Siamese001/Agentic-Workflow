"""R12 REPLAY AND AUDIT SEALING (spec lines 569–584, 699–702).

Builds a ``ReplayEnvelope`` and computes the canonical ``compliance_hash``
over the deterministic JSON serialization of the envelope (sans hash).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any, Mapping

from agentic_core.L5_safety.v5.contracts import (
    GovernanceReviewRequest,
    ReplayEnvelope,
    StandardsFingerprint,
)
from agentic_core.L5_safety.v5.types import DecisionVerdict


REPLAY_SCHEMA_VERSION = "v5.0"


def _canonical_json(payload: Mapping[str, Any]) -> str:
    """RFC 8785-flavored canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def seal_replay_envelope(
    *,
    request: GovernanceReviewRequest,
    decision_verdict: DecisionVerdict,
    standards_fingerprint: StandardsFingerprint,
    span_id: str,
    route_id: str,
    capability_token_hash: str = "",
    sandbox_envelope_hash: str = "",
    prompt_artifact_hash: str = "",
    evidence_contract_hash: str = "",
    output_schema_hash: str = "",
    tool_invocation_hashes: tuple[str, ...] = (),
    model_invocation_hashes: tuple[str, ...] = (),
    state_diff_hash: str = "",
    human_disposition_hash: str = "",
) -> ReplayEnvelope:
    """Build and seal a v5 replay envelope.

    `compliance_hash` = sha256(canonical_json(envelope without hash))
    """
    draft = ReplayEnvelope(
        schema_version=REPLAY_SCHEMA_VERSION,
        request_id=request.request_id,
        run_id=request.run_id,
        trace_id=request.trace_id,
        span_id=span_id,
        route_id=route_id,
        policy_hash=request.policy_hash,
        blueprint_hash=request.blueprint_hash,
        registry_digest_set=tuple(request.registry_digest_set),
        capability_token_hash=capability_token_hash,
        sandbox_envelope_hash=sandbox_envelope_hash,
        prompt_artifact_hash=prompt_artifact_hash,
        evidence_contract_hash=evidence_contract_hash,
        output_schema_hash=output_schema_hash,
        tool_invocation_hashes=tuple(tool_invocation_hashes),
        model_invocation_hashes=tuple(model_invocation_hashes),
        state_diff_hash=state_diff_hash,
        human_disposition_hash=human_disposition_hash,
        decision_verdict=decision_verdict,
        standards_fingerprint=standards_fingerprint,
        compliance_hash="",
    )
    payload = draft.to_dict()
    payload.pop("compliance_hash", None)
    h = _sha256(_canonical_json(payload))
    return replace(draft, compliance_hash=h)


def build_audit_log_event(
    *,
    request: GovernanceReviewRequest,
    decision: DecisionVerdict,
    reason_codes: tuple[str, ...],
    compliance_hash: str,
    actor: str,
    timestamp_iso: str,
) -> dict[str, Any]:
    """Build an append-only audit log event (spec lines 694–697).

    Pure function — caller persists.
    """
    return {
        "actor": actor,
        "compliance_hash": compliance_hash,
        "decision": decision.value,
        "reason_codes": sorted(reason_codes),
        "request_id": request.request_id,
        "run_id": request.run_id,
        "tenant_id": request.tenant_id,
        "timestamp_iso": timestamp_iso,
        "trace_id": request.trace_id,
    }


__all__ = [
    "REPLAY_SCHEMA_VERSION",
    "build_audit_log_event",
    "seal_replay_envelope",
]
