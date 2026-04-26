"""v6 §5.7 — Return Payload + Runtime Exhaust Manifest + Runtime Boundary.

Implements the spec at
``docs/reference/05_Exit_Evaluation_&_Control/05.7_Exit_Return_Response_and_Runtime_Exhaust_detailed.md``.

This module owns:
- final caller return payload packaging (per-disposition shape rules)
- safe abstain / safe partial packaging
- committed artifact reference rule (UWG receipt required)
- disposition receipt exposure policy
- runtime exhaust manifest sealing
- completed-run boundary handoff to L6

Hard rule: this module does NOT execute, retrieve, mutate, or assemble prompts.
It packages the disposition + sealed artifacts into a transport-safe shape.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateVerdict,
    V6Disposition,
    X3AllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3EscalatePacket,
    X3SafeAbstainPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.uwg import UwgOutcome, UwgReceipt


class RuntimeBoundaryStatus(str, Enum):
    """5.7 RUNTIME BOUNDARY status — sealed-or-not."""

    OPEN = "OPEN"
    SEALED = "SEALED"


# Spec §5.7 FAILURE MODES — emitted when a return-payload validation fails.
RETURN_PAYLOAD_FAILURE_CODES: frozenset[str] = frozenset(
    {
        "FINAL_RESPONSE_REFERENCES_UNCOMMITTED_ARTIFACT",
        "UNSAFE_CONTENT_IN_RETURN_PAYLOAD",
        "QUARANTINED_CONTENT_EXPOSED",
        "WEAK_SUPPORT_HIDDEN",
        "SYSTEM_PROMPT_LEAK_IN_RETURN",
        "EXHAUST_MANIFEST_MISSING",
        "RUNTIME_BOUNDARY_NOT_SEALED",
        "L6_LIVE_MUTATION_ATTEMPT",
        "COMMIT_STATUS_MISREPRESENTED",
        "DISPOSITION_RECEIPT_MISSING",
    }
)


@dataclass(slots=True)
class ReturnPayload:
    """Spec §5.7 — final caller return payload.

    Fields are dispositional. The ``disposition`` field is always set; the
    other fields are populated only when relevant per the per-disposition
    rules in the spec (X3D ALLOW / FINISH, X3E SAFE ABSTAIN / CLARIFY, etc).
    """

    disposition: V6Disposition
    disposition_receipt_ref: str = ""
    trace_root: str = ""
    runtime_exhaust_manifest_ref: str = ""

    # X3D — final response packaging
    final_response_ref: str = ""
    final_response_text: str = ""
    response_schema_status: str = ""
    evidence_status: str = ""
    citation_refs: list[str] = field(default_factory=list)
    caveat_refs: list[str] = field(default_factory=list)
    commit_receipt_id: str = ""

    # X3E — safe abstain / clarify packaging
    abstain_reason: str = ""
    minimal_clarification_question: str = ""
    safe_alternative_ref: str = ""
    bounded_explanation: str = ""
    failed_support_target: str = ""
    no_commit_request: bool = False

    # X3A — safe deny / reroute packaging
    deny_reason_category: str = ""
    safe_partial_artifact_id: str = ""
    replan_hint: str = ""
    no_durable_write_assertion: bool = True

    # X3B — human review packaging
    pending_human_review: bool = False
    review_packet_id: str = ""

    # X3C — commit-request packaging (only meaningful once UWG resolved)
    commit_status: str = ""  # ACCEPTED | REJECTED | HELD | PENDING

    # Failure modes raised during return-payload validation
    failure_codes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RuntimeExhaustManifest:
    """Spec §5.7 RUNTIME EXHAUST MANIFEST — sealed completed-run evidence for L6.

    Sealed AFTER the final X3 disposition is emitted. L6 may ingest this but
    cannot mutate the current run.
    """

    exhaust_manifest_id: str
    request_id: str
    run_id: str
    session_id: str = ""
    trace_root: str = ""
    x3_disposition_receipt_ref: str = ""
    x3_disposition_value: str = ""
    exit_review_packet_ref: str = ""
    x1_gate_result_bundle_ref: str = ""
    x2_aggregate_decision_ref: str = ""
    l2_artifact_refs: list[str] = field(default_factory=list)
    l3_workflow_package_ref: str = ""
    ret_packet_ref: str = ""
    hitl_packet_refs: list[str] = field(default_factory=list)
    commit_receipt_refs: list[str] = field(default_factory=list)
    uwg_receipt_refs: list[str] = field(default_factory=list)
    route_contract_ref: str = ""
    c0_evidence_contract_refs: list[str] = field(default_factory=list)
    prompt_artifact_refs: list[str] = field(default_factory=list)
    grader_result_refs: list[str] = field(default_factory=list)
    replay_digest_refs: list[str] = field(default_factory=list)
    otel_span_refs: list[str] = field(default_factory=list)
    anomaly_signal_refs: list[str] = field(default_factory=list)
    cost_latency_token_metrics: dict[str, Any] = field(default_factory=dict)
    runtime_boundary_status: RuntimeBoundaryStatus = RuntimeBoundaryStatus.SEALED
    l6_handoff_allowed: bool = True
    deterministic_digest: str = ""
    sealed_at: int = 0


# ---- helpers --------------------------------------------------------------


def _disposition_receipt_id(packet: ExitReviewPacket, disposition: V6Disposition) -> str:
    """Stable disposition-receipt id derived from replay_key + run + disposition."""
    raw = f"{packet.replay_key}|{packet.run_id}|{disposition.value}".encode("utf-8")
    return f"x3-{hashlib.sha256(raw).hexdigest()[:16]}"


def _exhaust_manifest_id(packet: ExitReviewPacket) -> str:
    raw = f"exhaust|{packet.replay_key}|{packet.run_id}".encode("utf-8")
    return f"exh-{hashlib.sha256(raw).hexdigest()[:16]}"


# Lightweight redaction for prompt-leak markers in returned text.
# Markers are pre-lowercased so the comparison is case-insensitive.
_LEAK_MARKERS = (
    "you are an ai assistant designed to",
    "your instructions are to",
    "developer:",
    "system prompt:",
)


def _has_system_prompt_leak(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _LEAK_MARKERS)


def _is_quarantined(packet: ExitReviewPacket) -> bool:
    out = packet.output or {}
    et = packet.exec_trace or {}
    return bool(out.get("quarantined") or et.get("quarantined_payload_refs"))


# ---- per-disposition builders --------------------------------------------


def _build_allow_payload(
    packet: ExitReviewPacket,
    x3_packet: X3AllowPacket,
    *,
    receipt_id: str,
    exhaust_id: str,
) -> ReturnPayload:
    """Spec §5.7 X3D ALLOW / FINISH RETURN."""
    out = packet.output or {}
    fec = packet.final_evidence_contract or {}
    payload = ReturnPayload(
        disposition=V6Disposition.ALLOW,
        disposition_receipt_ref=receipt_id,
        trace_root=packet.trace_root,
        runtime_exhaust_manifest_ref=exhaust_id,
        final_response_text=str(x3_packet.final_response or out.get("text", "")),
        final_response_ref=str(out.get("response_ref", "") or x3_packet.commit_receipt_id or ""),
        response_schema_status=x3_packet.schema_status,
        evidence_status=x3_packet.evidence_status or str(fec.get("c0_status", "")),
        citation_refs=list(out.get("citation_refs", []) or []),
        caveat_refs=list(out.get("caveat_refs", []) or []),
        commit_receipt_id=x3_packet.commit_receipt_id,
    )
    # Spec: X3D MAY reference committed artifact only if UWG receipt exists.
    if payload.commit_receipt_id and not str(payload.commit_receipt_id).startswith("uwg-"):
        # Soft-validate: a committed-artifact reference must look like a UWG id.
        # We don't require a specific prefix at runtime; the actual check is
        # done by ``validate_return_payload`` against a UwgReceipt object.
        pass
    return payload


def _build_safe_abstain_payload(
    packet: ExitReviewPacket,
    x3_packet: X3SafeAbstainPacket,
    *,
    receipt_id: str,
    exhaust_id: str,
) -> ReturnPayload:
    """Spec §5.7 X3E SAFE ABSTAIN / CLARIFY RETURN."""
    return ReturnPayload(
        disposition=V6Disposition.SAFE_ABSTAIN,
        disposition_receipt_ref=receipt_id,
        trace_root=packet.trace_root,
        runtime_exhaust_manifest_ref=exhaust_id,
        abstain_reason=x3_packet.abstain_reason,
        minimal_clarification_question=x3_packet.minimal_clarification_question,
        safe_alternative_ref=x3_packet.safe_alternative,
        bounded_explanation=x3_packet.abstain_reason,
        failed_support_target=x3_packet.failed_support_target,
        no_commit_request=True,
    )


def _build_deny_payload(
    packet: ExitReviewPacket,
    x3_packet: X3DenyPacket,
    *,
    receipt_id: str,
    exhaust_id: str,
) -> ReturnPayload:
    """Spec §5.7 X3A SAFE DENY / REROUTE RETURN."""
    # Spec rule: return reason category, not raw internal policy dump.
    category = (
        "DENY_SAFE_PARTIAL"
        if x3_packet.sub_disposition == "DENY_SAFE_PARTIAL"
        else x3_packet.sub_disposition or "DENY_STOP"
    )
    return ReturnPayload(
        disposition=V6Disposition.DENY,
        disposition_receipt_ref=receipt_id,
        trace_root=packet.trace_root,
        runtime_exhaust_manifest_ref=exhaust_id,
        deny_reason_category=category,
        safe_partial_artifact_id=x3_packet.safe_partial_artifact_id,
        replan_hint=x3_packet.replan_hint,
        no_durable_write_assertion=True,
    )


def _build_escalate_payload(
    packet: ExitReviewPacket,
    x3_packet: X3EscalatePacket,
    *,
    receipt_id: str,
    exhaust_id: str,
) -> ReturnPayload:
    """Spec §5.7 X3B HUMAN REVIEW RETURN."""
    return ReturnPayload(
        disposition=V6Disposition.ESCALATE,
        disposition_receipt_ref=receipt_id,
        trace_root=packet.trace_root,
        runtime_exhaust_manifest_ref=exhaust_id,
        pending_human_review=True,
        review_packet_id=x3_packet.review_packet_id,
        no_durable_write_assertion=True,
    )


def _build_commit_request_payload(
    packet: ExitReviewPacket,
    x3_packet: X3CommitRequestPacket,
    *,
    receipt_id: str,
    exhaust_id: str,
    uwg_receipt: UwgReceipt | None = None,
) -> ReturnPayload:
    """Spec §5.7 X3C COMMIT REQUEST RETURN.

    By itself X3C is not user-facing success. Only when a UWG receipt is
    attached do we expose the commit_receipt_id; otherwise commit_status is
    PENDING and no committed artifact is referenced.
    """
    del x3_packet  # signature parity with sibling builders; UWG receipt is authoritative
    payload = ReturnPayload(
        disposition=V6Disposition.COMMIT_REQUEST,
        disposition_receipt_ref=receipt_id,
        trace_root=packet.trace_root,
        runtime_exhaust_manifest_ref=exhaust_id,
        no_durable_write_assertion=False,  # mutation is the point of X3C
    )
    if uwg_receipt is None:
        payload.commit_status = "PENDING"
        return payload
    if uwg_receipt.outcome is UwgOutcome.COMMIT_ACCEPTED:
        payload.commit_status = "ACCEPTED"
        payload.commit_receipt_id = uwg_receipt.commit_request_id
        return payload
    if uwg_receipt.outcome is UwgOutcome.COMMIT_HELD:
        payload.commit_status = "HELD"
        payload.pending_human_review = True
        return payload
    payload.commit_status = "REJECTED"
    payload.deny_reason_category = uwg_receipt.rejected_reason
    return payload


def build_return_payload(
    packet: ExitReviewPacket,
    x3_packet: Any,
    *,
    uwg_receipt: UwgReceipt | None = None,
) -> ReturnPayload:
    """Dispatch to the correct per-disposition return-payload builder.

    Spec §5.7: package the X3 disposition + sealed artifacts into a
    transport-safe payload that respects the per-disposition rules.
    """
    if isinstance(x3_packet, X3AllowPacket):
        receipt_id = _disposition_receipt_id(packet, V6Disposition.ALLOW)
        exhaust_id = _exhaust_manifest_id(packet)
        return _build_allow_payload(packet, x3_packet, receipt_id=receipt_id, exhaust_id=exhaust_id)
    if isinstance(x3_packet, X3SafeAbstainPacket):
        receipt_id = _disposition_receipt_id(packet, V6Disposition.SAFE_ABSTAIN)
        exhaust_id = _exhaust_manifest_id(packet)
        return _build_safe_abstain_payload(packet, x3_packet, receipt_id=receipt_id, exhaust_id=exhaust_id)
    if isinstance(x3_packet, X3DenyPacket):
        receipt_id = _disposition_receipt_id(packet, V6Disposition.DENY)
        exhaust_id = _exhaust_manifest_id(packet)
        return _build_deny_payload(packet, x3_packet, receipt_id=receipt_id, exhaust_id=exhaust_id)
    if isinstance(x3_packet, X3EscalatePacket):
        receipt_id = _disposition_receipt_id(packet, V6Disposition.ESCALATE)
        exhaust_id = _exhaust_manifest_id(packet)
        return _build_escalate_payload(packet, x3_packet, receipt_id=receipt_id, exhaust_id=exhaust_id)
    if isinstance(x3_packet, X3CommitRequestPacket):
        receipt_id = _disposition_receipt_id(packet, V6Disposition.COMMIT_REQUEST)
        exhaust_id = _exhaust_manifest_id(packet)
        return _build_commit_request_payload(
            packet,
            x3_packet,
            receipt_id=receipt_id,
            exhaust_id=exhaust_id,
            uwg_receipt=uwg_receipt,
        )
    raise TypeError(f"unknown X3 packet shape: {type(x3_packet).__name__}")


def validate_return_payload(
    payload: ReturnPayload,
    packet: ExitReviewPacket,
    *,
    uwg_receipt: UwgReceipt | None = None,
) -> list[str]:
    """Run §5.7 return-payload validation.

    Returns a list of failure codes from ``RETURN_PAYLOAD_FAILURE_CODES``;
    empty list means the payload is safe to return. Detected failures are
    also written into ``payload.failure_codes`` so callers can inspect.
    """
    failures: list[str] = []

    # 1. Disposition receipt must exist.
    if not payload.disposition_receipt_ref:
        failures.append("DISPOSITION_RECEIPT_MISSING")

    # 2. Final answer cannot reference an uncommitted artifact (X3D + commit ref).
    if payload.disposition is V6Disposition.ALLOW and payload.commit_receipt_id and uwg_receipt is None:
        failures.append("FINAL_RESPONSE_REFERENCES_UNCOMMITTED_ARTIFACT")

    # 3. X3C must misrepresent nothing — commit_status must align with receipt.
    if payload.disposition is V6Disposition.COMMIT_REQUEST:
        if uwg_receipt is None and payload.commit_status not in {"PENDING", ""}:
            failures.append("COMMIT_STATUS_MISREPRESENTED")
        elif uwg_receipt is not None:
            expected = {
                UwgOutcome.COMMIT_ACCEPTED: "ACCEPTED",
                UwgOutcome.COMMIT_HELD: "HELD",
                UwgOutcome.COMMIT_REJECTED: "REJECTED",
            }[uwg_receipt.outcome]
            if payload.commit_status != expected:
                failures.append("COMMIT_STATUS_MISREPRESENTED")

    # 4. Quarantined content must not appear in any returned text field.
    if _is_quarantined(packet) and payload.final_response_text:
        failures.append("QUARANTINED_CONTENT_EXPOSED")

    # 5. System-prompt leak in final response.
    if payload.final_response_text and _has_system_prompt_leak(payload.final_response_text):
        failures.append("SYSTEM_PROMPT_LEAK_IN_RETURN")

    # 6. Weak support hidden — X3D with weak evidence and no caveat exposed.
    if payload.disposition is V6Disposition.ALLOW:
        fec = packet.final_evidence_contract or {}
        c0 = str(fec.get("c0_status", "")).upper()
        if c0 == "WEAK_WITH_CAVEATS" and not payload.caveat_refs:
            failures.append("WEAK_SUPPORT_HIDDEN")

    # 7. Safe abstain MUST NOT carry a commit request.
    if payload.disposition is V6Disposition.SAFE_ABSTAIN and payload.commit_receipt_id:
        failures.append("UNSAFE_CONTENT_IN_RETURN_PAYLOAD")

    payload.failure_codes = list(failures)
    return failures


def seal_runtime_exhaust(
    packet: ExitReviewPacket,
    x3_packet: Any,
    verdicts: list[GateVerdict],
    *,
    uwg_receipt: UwgReceipt | None = None,
    sealed_at: int | None = None,
) -> RuntimeExhaustManifest:
    """Spec §5.7 RUNTIME EXHAUST MANIFEST — seal the completed-run evidence.

    Called only after the X3 disposition has been emitted. The manifest is
    immutable from this point: L6 may read it, but cannot mutate the run.
    """
    disposition: V6Disposition = getattr(x3_packet, "disposition", V6Disposition.DENY)
    receipt_id = _disposition_receipt_id(packet, disposition)
    exhaust_id = _exhaust_manifest_id(packet)
    spans = (packet.otel_spans or {}).get("spans", {}) or {}
    span_refs: list[str] = []
    for k, v in spans.items():
        if isinstance(v, list):
            span_refs.extend(f"{k}:{x}" for x in v)
        else:
            span_refs.append(f"{k}:{v}")
    digest_payload = {
        "rk": packet.replay_key,
        "rid": packet.run_id,
        "disp": disposition.value,
        "policy": packet.policy_hash,
        "blueprint": packet.blueprint_hash,
        "receipt": receipt_id,
    }
    digest = hashlib.sha256(json.dumps(digest_payload, sort_keys=True).encode("utf-8")).hexdigest()

    return RuntimeExhaustManifest(
        exhaust_manifest_id=exhaust_id,
        request_id=packet.request_id,
        run_id=packet.run_id,
        session_id=packet.session_id,
        trace_root=packet.trace_root,
        x3_disposition_receipt_ref=receipt_id,
        x3_disposition_value=disposition.value,
        exit_review_packet_ref=f"erp::{packet.replay_key}",
        x1_gate_result_bundle_ref=f"x1bundle::{packet.replay_key}",
        x2_aggregate_decision_ref=f"x2::{packet.replay_key}",
        l2_artifact_refs=[ref for ref in (packet.exec_trace or {}).get("sealed_l2_artifact_refs", []) or []],
        l3_workflow_package_ref=str((packet.exec_trace or {}).get("workflow_package_ref", "")),
        ret_packet_ref=str((packet.exec_trace or {}).get("ret_packet_ref", "")),
        hitl_packet_refs=[ref for ref in (packet.hitl_packet or {}).get("refs", []) or []],
        commit_receipt_refs=(
            [uwg_receipt.commit_request_id] if uwg_receipt and uwg_receipt.commit_request_id else []
        ),
        uwg_receipt_refs=(
            [f"uwg::{uwg_receipt.outcome.value}::{uwg_receipt.ledger_seq}"] if uwg_receipt else []
        ),
        route_contract_ref=str((packet.route_contract or {}).get("route_id", "")),
        c0_evidence_contract_refs=list((packet.final_evidence_contract or {}).get("contract_refs", []) or []),
        prompt_artifact_refs=list((packet.compiled_prompt_artifact or {}).get("artifact_refs", []) or []),
        grader_result_refs=[v.gate_id for v in verdicts],
        replay_digest_refs=[packet.replay_key] if packet.replay_key else [],
        otel_span_refs=span_refs,
        anomaly_signal_refs=list(packet.anomaly_flags or []),
        cost_latency_token_metrics={
            "cost_tier": packet.cost_tier,
            "timeout_ms": packet.timeout_ms,
            "budget_counters": dict(packet.budget_counters or {}),
        },
        runtime_boundary_status=RuntimeBoundaryStatus.SEALED,
        l6_handoff_allowed=True,
        deterministic_digest=digest,
        sealed_at=int(sealed_at if sealed_at is not None else time.time()),
    )


def close_runtime_boundary(
    payload: ReturnPayload,
    manifest: RuntimeExhaustManifest,
) -> bool:
    """Spec §5.7 RUNTIME BOUNDARY — close after disposition + return + seal.

    Returns True iff all four close conditions hold:
    1. X3 disposition receipt emitted.
    2. ReturnPayload produced or withheld by policy (we always produce one).
    3. Commit path resolved (X3C without UWG = PENDING is an allowed terminal).
    4. RuntimeExhaustManifest sealed.
    """
    if not payload.disposition_receipt_ref:
        return False
    if not manifest.exhaust_manifest_id:
        return False
    if manifest.runtime_boundary_status is not RuntimeBoundaryStatus.SEALED:
        return False
    return True


def enqueue_l6_handoff(
    manifest: RuntimeExhaustManifest,
) -> dict[str, Any]:
    """Spec §5.7 L6 HANDOFF — produce a sealed handoff packet.

    L6 may ingest the manifest, evaluate, calibrate, RCA, and seek future-run
    promotion. L6 may NOT mutate the completed current run.
    """
    if not manifest.l6_handoff_allowed:
        raise RuntimeError("manifest forbids L6 handoff")
    return {
        "exhaust_manifest_id": manifest.exhaust_manifest_id,
        "run_id": manifest.run_id,
        "trace_root": manifest.trace_root,
        "disposition": manifest.x3_disposition_value,
        "deterministic_digest": manifest.deterministic_digest,
        "l6_mutation_allowed": False,
        "handoff_at": int(time.time()),
    }


__all__ = [
    "RETURN_PAYLOAD_FAILURE_CODES",
    "ReturnPayload",
    "RuntimeBoundaryStatus",
    "RuntimeExhaustManifest",
    "build_return_payload",
    "close_runtime_boundary",
    "enqueue_l6_handoff",
    "seal_runtime_exhaust",
    "validate_return_payload",
]
