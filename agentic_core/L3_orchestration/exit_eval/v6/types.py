"""v6 Exit Evaluation — shared types.

Implements the spec at
``docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v6.md``
sections X1, X2, X3 and the *Gate verdict format* contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SourceType(str, Enum):
    """5.1 N1 source classification."""

    L2_SEALED_ARTIFACT = "L2_SEALED_ARTIFACT"
    L3_WORKFLOW_PACKAGE = "L3_WORKFLOW_PACKAGE"
    RET_CACHE_EXACT = "RET_CACHE_EXACT"
    RET_CACHE_SEMANTIC = "RET_CACHE_SEMANTIC"
    RET_FALLBACK = "RET_FALLBACK"
    HITL_RECLEARED_PACKET = "HITL_RECLEARED_PACKET"


class GateResult(str, Enum):
    """Spec X1 *Result enum* — bounded gate outcome."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class V6Disposition(str, Enum):
    """v6 X3 dispositions. Distinct from v4/v5 break-glass semantics.

    Spec §X3: every run exits exactly one of these.
    """

    DENY = "X3A"  # deny / reroute
    ESCALATE = "X3B"  # HITL escalation + H1-H4 + L5 re-clearance
    COMMIT_REQUEST = "X3C"  # hand off to UWG; UWG is sole ink path
    ALLOW = "X3D"  # answer-only, no durable write
    SAFE_ABSTAIN = "X3E"  # safe abstain / clarify — v6 redefines X3E


@dataclass(slots=True)
class GateVerdict:
    """Spec §X1 *Gate verdict format* — every gate produces this shape."""

    gate_id: str  # X1A..X1J
    result: GateResult
    severity: str = "info"  # info | warn | alert
    reason_codes: list[str] = field(default_factory=list)
    score: float = 0.0
    threshold: float = 0.0
    grader_type: str = "code"  # code | LLM-judge | hybrid | human-calibrated
    evidence_refs: list[str] = field(default_factory=list)
    replay_refs: list[str] = field(default_factory=list)
    confidence: float = 1.0
    abstain_flag: bool = False
    remediation_hint: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExitReviewPacket:
    """Output of 5.1 N1-N5 normalization — single shape for every source.

    Field names mirror the receipt fields enumerated in spec §5.0 INPUTS RECEIVED.
    """

    # 5.1 N1 source classification
    source_type: SourceType

    # Identity / replay (5.0 required receipts)
    request_id: str = ""
    run_id: str = ""
    session_id: str = ""
    trace_root: str = ""
    route_id: str = ""

    # Hashes
    policy_hash: str = ""
    blueprint_hash: str = ""
    prompt_hash: str = ""
    replay_key: str = ""
    compliance_hash: str = ""
    manifest_hash: str = ""
    hmac_sig: str = ""

    # Authority envelopes
    route_contract: dict[str, Any] = field(default_factory=dict)
    sandbox_envelope: dict[str, Any] = field(default_factory=dict)
    capability_token: dict[str, Any] = field(default_factory=dict)
    provider_lane: str = ""

    # Budget
    cost_tier: str = ""
    slo_slice: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 0
    budget_counters: dict[str, Any] = field(default_factory=dict)

    # Terminal classification + work product
    terminal_class: str = ""  # answer_only | with_state_diff | abstain | ...
    exec_trace: dict[str, Any] = field(default_factory=dict)
    state_diff: dict[str, Any] = field(default_factory=dict)
    write_intent_class: str = ""
    evidence_bundle: dict[str, Any] = field(default_factory=dict)
    final_evidence_contract: dict[str, Any] = field(default_factory=dict)
    prompt_assembly_status: dict[str, Any] = field(default_factory=dict)
    compiled_prompt_artifact: dict[str, Any] = field(default_factory=dict)

    # Output / scoring
    output: dict[str, Any] = field(default_factory=dict)
    validation_counters: dict[str, Any] = field(default_factory=dict)
    retry_counters: dict[str, Any] = field(default_factory=dict)
    repair_counters: dict[str, Any] = field(default_factory=dict)
    trajectory_snapshot: dict[str, Any] = field(default_factory=dict)
    grader_composition: dict[str, Any] = field(default_factory=dict)
    track_label: str = "production"  # capability | regression | production | shadow-candidate
    support_score: float = 0.0
    confidence: float = 0.0
    abstain_flags: list[str] = field(default_factory=list)
    contradiction_flags: list[str] = field(default_factory=list)

    # Observability
    otel_spans: dict[str, Any] = field(default_factory=dict)
    timing_offsets: dict[str, Any] = field(default_factory=dict)
    anomaly_flags: list[str] = field(default_factory=list)

    # HITL prior
    hitl_packet: dict[str, Any] = field(default_factory=dict)

    # Live control signals (5.1 N5)
    bus_d_signals: list[str] = field(default_factory=list)
    bus_e_signals: list[str] = field(default_factory=list)
    replay_guard_violations: list[str] = field(default_factory=list)
    isolation_anomalies: list[str] = field(default_factory=list)
    drift_warnings: list[str] = field(default_factory=list)


# ---- X3 disposition packets (required-output shapes from spec §X3) ----


@dataclass(slots=True)
class X3DenyPacket:
    """Spec §X3A required output packet."""

    disposition: V6Disposition = V6Disposition.DENY
    sub_disposition: str = "DENY_STOP"  # DENY_STOP|DENY_SAFE_PARTIAL|REROUTE_*
    reason_codes: list[str] = field(default_factory=list)
    failed_gate_ids: list[str] = field(default_factory=list)
    user_safe_message: str = ""
    safe_partial_artifact_id: str = ""
    replan_hint: str = ""
    l6_failure_packet: dict[str, Any] = field(default_factory=dict)
    trace_root: str = ""


@dataclass(slots=True)
class X3EscalatePacket:
    """Spec §X3B required output packet."""

    disposition: V6Disposition = V6Disposition.ESCALATE
    trigger_reasons: list[str] = field(default_factory=list)
    review_packet_id: str = ""
    h1_freeze_state: dict[str, Any] = field(default_factory=dict)
    review_packet_contents: dict[str, Any] = field(default_factory=dict)
    trace_root: str = ""


@dataclass(slots=True)
class X3CommitRequestPacket:
    """Spec §X3C UWG handoff packet."""

    disposition: V6Disposition = V6Disposition.COMMIT_REQUEST
    commit_request_id: str = ""
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    route_contract: dict[str, Any] = field(default_factory=dict)
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""
    compliance_hash: str = ""
    hmac_sig: str = ""
    capability_token: dict[str, Any] = field(default_factory=dict)
    state_diff: dict[str, Any] = field(default_factory=dict)
    write_intent_class: str = ""
    before_snapshot: dict[str, Any] = field(default_factory=dict)
    after_proposed_snapshot: dict[str, Any] = field(default_factory=dict)
    rollback_plan: dict[str, Any] = field(default_factory=dict)
    blast_radius: str = ""
    evidence_citation_map: dict[str, Any] = field(default_factory=dict)
    hitl_decision_receipt: dict[str, Any] = field(default_factory=dict)
    grader_verdict_bundle: list[GateVerdict] = field(default_factory=list)
    pass_k_consistency_receipt: dict[str, Any] = field(default_factory=dict)
    replay_determinism_digest: str = ""
    trace_evidence_seal: str = ""


@dataclass(slots=True)
class X3AllowPacket:
    """Spec §X3D required output packet."""

    disposition: V6Disposition = V6Disposition.ALLOW
    final_response: str = ""
    schema_status: str = "valid"
    evidence_status: str = ""
    commit_receipt_id: str = ""
    trace_root: str = ""
    runtime_exhaust_manifest: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class X3SafeAbstainPacket:
    """Spec §X3E required output packet."""

    disposition: V6Disposition = V6Disposition.SAFE_ABSTAIN
    abstain_reason: str = ""
    minimal_clarification_question: str = ""
    safe_alternative: str = ""
    failed_support_target: str = ""
    trace_root: str = ""


__all__ = [
    "SourceType",
    "GateResult",
    "GateVerdict",
    "V6Disposition",
    "ExitReviewPacket",
    "X3DenyPacket",
    "X3EscalatePacket",
    "X3CommitRequestPacket",
    "X3AllowPacket",
    "X3SafeAbstainPacket",
]
