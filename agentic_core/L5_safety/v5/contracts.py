"""v5 wire dataclasses.

Each dataclass is frozen and emits a deterministic ``to_dict``. Together
they form the v5 GovernanceReviewRequest → GovernanceResult shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.L5_safety.v5.types import (
    BoundaryClassification,
    DecisionVerdict,
    GovernanceMode,
    NextLane,
    OriginLabel,
    PacketKind,
    ReasonCode,
    ReviewDepth,
    RiskTierBandV5,
    SideEffectClass,
    StandardsTag,
    TriageFlag,
)


def _sorted_strings(values: tuple[str, ...]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class GovernanceReviewRequest:
    """Spec G0 OUTPUT — normalized, typed, bounded review packet.

    Required fields (G0 lines 33–38) all explicit. Optional fields use
    safe empty defaults so callers can build a partial packet, then fail
    deterministically inside ``g0_entry.validate_entry_packet``.
    """

    request_id: str
    trace_id: str
    run_id: str
    tenant_id: str
    caller_id: str
    packet_kind: PacketKind
    side_effect_class: SideEffectClass

    # Authority requested (G0 line 38)
    requested_authority: tuple[str, ...] = field(default_factory=tuple)

    # Hashes / digests (G0 line 36)
    policy_hash: str = ""
    blueprint_hash: str = ""
    registry_digest_set: tuple[str, ...] = field(default_factory=tuple)
    route_contract_hmac: str = ""
    replay_key: str = ""

    # Origin manifest (raw, pre-G2a). Map of origin label → list of field paths.
    origin_trust_manifest_raw: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    # Principal chain compaction (full chain held in v4 token if any)
    principal_chain_id: str = ""

    # Free-form payload kept opaque to the validator. Callers pass already-
    # sanitized data; this field is used only for hashing into replay.
    payload_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_hash": self.blueprint_hash,
            "caller_id": self.caller_id,
            "origin_trust_manifest_raw": {
                k: _sorted_strings(tuple(v)) for k, v in self.origin_trust_manifest_raw.items()
            },
            "packet_kind": self.packet_kind.value,
            "payload_digest": self.payload_digest,
            "policy_hash": self.policy_hash,
            "principal_chain_id": self.principal_chain_id,
            "registry_digest_set": _sorted_strings(self.registry_digest_set),
            "replay_key": self.replay_key,
            "request_id": self.request_id,
            "requested_authority": _sorted_strings(self.requested_authority),
            "route_contract_hmac": self.route_contract_hmac,
            "run_id": self.run_id,
            "side_effect_class": self.side_effect_class.value,
            "tenant_id": self.tenant_id,
            "trace_id": self.trace_id,
        }


@dataclass(frozen=True)
class TriageReport:
    """Spec G1 OUTPUT (lines 82–87)."""

    governance_mode: GovernanceMode
    risk_tier_band: RiskTierBandV5
    review_depth: ReviewDepth
    triage_flags: tuple[TriageFlag, ...]
    next_lane: NextLane

    def to_dict(self) -> dict[str, Any]:
        return {
            "governance_mode": self.governance_mode.value,
            "next_lane": self.next_lane.value,
            "review_depth": self.review_depth.value,
            "risk_tier_band": self.risk_tier_band.value,
            "triage_flags": sorted(f.value for f in self.triage_flags),
        }


@dataclass(frozen=True)
class OriginTrustManifest:
    """Spec G2a OUTPUT (lines 186–190)."""

    labeled_fields: Mapping[OriginLabel, tuple[str, ...]]
    boundary_classification: BoundaryClassification
    sanitized_payload_map: Mapping[str, str] = field(default_factory=dict)
    quarantine_reasons: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_classification": self.boundary_classification.value,
            "labeled_fields": {
                label.value: _sorted_strings(tuple(fields)) for label, fields in self.labeled_fields.items()
            },
            "quarantine_reasons": sorted(self.quarantine_reasons),
            "sanitized_payload_map": dict(self.sanitized_payload_map),
        }


@dataclass(frozen=True)
class CapabilityTokenV5:
    """Spec R7 + GovernanceResult.capability_token (lines 442–453, 704–715).

    A v5 wire shape distinct from ``CapabilityTokenV4Artifact``. The v4
    token can be embedded by reference via ``v4_token_id`` when v5 is
    invoked from a v4-aware site.
    """

    token_id: str
    principal_chain_id: str
    scope: tuple[str, ...]
    ttl_seconds: int
    single_use: bool
    max_invocations: int
    connector_allowlist: tuple[str, ...]
    plan_digest: str
    route_contract_digest: str
    evidence_contract_id: str
    permission_ladder: tuple[str, ...]
    allowed_args_hash: str
    revocation_posture: str
    v4_token_id: str = ""

    def __post_init__(self) -> None:
        if not self.token_id:
            raise ValueError("CapabilityTokenV5: token_id required")
        if self.ttl_seconds < 0:
            raise ValueError("CapabilityTokenV5: ttl_seconds must be >= 0")
        if self.max_invocations < 1:
            raise ValueError("CapabilityTokenV5: max_invocations must be >= 1")
        if self.single_use and self.max_invocations != 1:
            raise ValueError(
                "CapabilityTokenV5: single_use implies max_invocations==1",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_args_hash": self.allowed_args_hash,
            "connector_allowlist": _sorted_strings(self.connector_allowlist),
            "evidence_contract_id": self.evidence_contract_id,
            "max_invocations": self.max_invocations,
            "permission_ladder": list(self.permission_ladder),
            "plan_digest": self.plan_digest,
            "principal_chain_id": self.principal_chain_id,
            "revocation_posture": self.revocation_posture,
            "route_contract_digest": self.route_contract_digest,
            "scope": _sorted_strings(self.scope),
            "single_use": self.single_use,
            "token_id": self.token_id,
            "ttl_seconds": self.ttl_seconds,
            "v4_token_id": self.v4_token_id,
        }


@dataclass(frozen=True)
class SandboxEnvelope:
    """Spec R7 sandbox_envelope (lines 455–461) + GovernanceResult (lines 717–726)."""

    fs_scope: tuple[str, ...]
    net_scope: tuple[str, ...]
    syscall_scope: tuple[str, ...]
    env_scope: tuple[str, ...]
    timeout_seconds: int
    memory_mb: int
    cpu_quota: float
    token_budget: int
    cost_budget_usd: float
    retry_budget: int
    artifact_scope: tuple[str, ...]
    output_sealing_path: str

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("SandboxEnvelope: timeout_seconds must be > 0")
        if self.memory_mb <= 0:
            raise ValueError("SandboxEnvelope: memory_mb must be > 0")
        if self.cpu_quota <= 0:
            raise ValueError("SandboxEnvelope: cpu_quota must be > 0")
        if self.token_budget < 0:
            raise ValueError("SandboxEnvelope: token_budget must be >= 0")
        if self.cost_budget_usd < 0:
            raise ValueError("SandboxEnvelope: cost_budget_usd must be >= 0")
        if self.retry_budget < 0:
            raise ValueError("SandboxEnvelope: retry_budget must be >= 0")
        if not self.output_sealing_path:
            raise ValueError("SandboxEnvelope: output_sealing_path required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_scope": _sorted_strings(self.artifact_scope),
            "cost_budget_usd": self.cost_budget_usd,
            "cpu_quota": self.cpu_quota,
            "env_scope": _sorted_strings(self.env_scope),
            "fs_scope": _sorted_strings(self.fs_scope),
            "memory_mb": self.memory_mb,
            "net_scope": _sorted_strings(self.net_scope),
            "output_sealing_path": self.output_sealing_path,
            "retry_budget": self.retry_budget,
            "syscall_scope": _sorted_strings(self.syscall_scope),
            "timeout_seconds": self.timeout_seconds,
            "token_budget": self.token_budget,
        }


@dataclass(frozen=True)
class StandardsFingerprint:
    """Spec G2 standards_fingerprint (line 108) + GovernanceResult (lines 686–692)."""

    tags: tuple[StandardsTag, ...]
    sector_overlay_ids: tuple[str, ...] = field(default_factory=tuple)
    internal_overlay_ids: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "internal_overlay_ids": _sorted_strings(self.internal_overlay_ids),
            "sector_overlay_ids": _sorted_strings(self.sector_overlay_ids),
            "tags": sorted(t.value for t in self.tags),
        }


@dataclass(frozen=True)
class HITLDispositionPacket:
    """Spec R10 OUTPUT (line 543).

    Bounded human-review packet. `re_clearance_required` is always True per
    spec — any human modification re-enters G2a / R1 / R5 / R6.
    """

    review_id: str
    reason: str
    proposed_action: str
    risk_summary: str
    alternatives: tuple[str, ...]
    decision: str  # APPROVE | MODIFY_DIFF | REJECT | REQUEST_MORE_INFO
    decision_rationale: str
    reviewer_id: str
    review_latency_ms: int
    re_clearance_required: bool = True

    def __post_init__(self) -> None:
        if self.decision not in {"APPROVE", "MODIFY_DIFF", "REJECT", "REQUEST_MORE_INFO"}:
            raise ValueError(
                f"HITLDispositionPacket: decision must be one of "
                f"APPROVE|MODIFY_DIFF|REJECT|REQUEST_MORE_INFO, got {self.decision!r}",
            )
        if self.review_latency_ms < 0:
            raise ValueError("HITLDispositionPacket: review_latency_ms must be >= 0")
        if not self.re_clearance_required:
            raise ValueError(
                "HITLDispositionPacket: re_clearance_required must be True "
                "(spec lines 540-543: human modification becomes untrusted data, "
                "re-enters G2a/R1/R5/R6)",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "alternatives": _sorted_strings(self.alternatives),
            "decision": self.decision,
            "decision_rationale": self.decision_rationale,
            "proposed_action": self.proposed_action,
            "re_clearance_required": self.re_clearance_required,
            "reason": self.reason,
            "review_id": self.review_id,
            "review_latency_ms": self.review_latency_ms,
            "reviewer_id": self.reviewer_id,
            "risk_summary": self.risk_summary,
        }


@dataclass(frozen=True)
class RuntimeRegressionReport:
    """Spec R11 OUTPUT (lines 547–566).

    Each boolean field answers the corresponding spec check. Composite
    ``passed`` is True iff every individual check is True.
    """

    policy_hash_unchanged: bool
    registry_digest_unchanged: bool
    provider_version_match: bool
    prompt_template_stable: bool
    tool_schema_unchanged: bool
    connector_grant_unchanged: bool
    sandbox_envelope_not_broadened: bool
    retry_loop_within_budget: bool
    cost_token_budget_within_limit: bool
    evidence_support_above_threshold: bool
    route_contract_not_reinterpreted: bool
    drift_reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return all(
            (
                self.policy_hash_unchanged,
                self.registry_digest_unchanged,
                self.provider_version_match,
                self.prompt_template_stable,
                self.tool_schema_unchanged,
                self.connector_grant_unchanged,
                self.sandbox_envelope_not_broadened,
                self.retry_loop_within_budget,
                self.cost_token_budget_within_limit,
                self.evidence_support_above_threshold,
                self.route_contract_not_reinterpreted,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector_grant_unchanged": self.connector_grant_unchanged,
            "cost_token_budget_within_limit": self.cost_token_budget_within_limit,
            "drift_reasons": sorted(self.drift_reasons),
            "evidence_support_above_threshold": self.evidence_support_above_threshold,
            "passed": self.passed,
            "policy_hash_unchanged": self.policy_hash_unchanged,
            "prompt_template_stable": self.prompt_template_stable,
            "provider_version_match": self.provider_version_match,
            "registry_digest_unchanged": self.registry_digest_unchanged,
            "retry_loop_within_budget": self.retry_loop_within_budget,
            "route_contract_not_reinterpreted": self.route_contract_not_reinterpreted,
            "sandbox_envelope_not_broadened": self.sandbox_envelope_not_broadened,
            "tool_schema_unchanged": self.tool_schema_unchanged,
        }


@dataclass(frozen=True)
class ReplayEnvelope:
    """Spec R12 + GovernanceResult.replay_envelope (lines 569–584, 699–702).

    `compliance_hash` is computed by ``replay_audit.seal_replay_envelope``
    over the canonical-JSON serialization of this struct (sans the hash
    field itself).
    """

    schema_version: str
    request_id: str
    run_id: str
    trace_id: str
    span_id: str
    route_id: str
    policy_hash: str
    blueprint_hash: str
    registry_digest_set: tuple[str, ...]
    capability_token_hash: str
    sandbox_envelope_hash: str
    prompt_artifact_hash: str
    evidence_contract_hash: str
    output_schema_hash: str
    tool_invocation_hashes: tuple[str, ...]
    model_invocation_hashes: tuple[str, ...]
    state_diff_hash: str
    human_disposition_hash: str
    decision_verdict: DecisionVerdict
    standards_fingerprint: StandardsFingerprint
    # Spec line 7: every certification binds principal chain.
    principal_chain_hash: str = ""
    compliance_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_hash": self.blueprint_hash,
            "capability_token_hash": self.capability_token_hash,
            "compliance_hash": self.compliance_hash,
            "decision_verdict": self.decision_verdict.value,
            "evidence_contract_hash": self.evidence_contract_hash,
            "human_disposition_hash": self.human_disposition_hash,
            "model_invocation_hashes": _sorted_strings(self.model_invocation_hashes),
            "output_schema_hash": self.output_schema_hash,
            "policy_hash": self.policy_hash,
            "principal_chain_hash": self.principal_chain_hash,
            "prompt_artifact_hash": self.prompt_artifact_hash,
            "registry_digest_set": _sorted_strings(self.registry_digest_set),
            "request_id": self.request_id,
            "route_id": self.route_id,
            "run_id": self.run_id,
            "sandbox_envelope_hash": self.sandbox_envelope_hash,
            "schema_version": self.schema_version,
            "span_id": self.span_id,
            "standards_fingerprint": self.standards_fingerprint.to_dict(),
            "state_diff_hash": self.state_diff_hash,
            "tool_invocation_hashes": _sorted_strings(self.tool_invocation_hashes),
            "trace_id": self.trace_id,
        }


@dataclass(frozen=True)
class GovernanceResult:
    """Spec OUTPUT CONTRACT (lines 655–757)."""

    decision: DecisionVerdict
    reason_codes: tuple[ReasonCode, ...]
    compliance_hash: str
    standards_fingerprint: StandardsFingerprint
    review_request: GovernanceReviewRequest
    triage: TriageReport
    origin_trust: OriginTrustManifest
    capability_token: CapabilityTokenV5 | None
    sandbox_envelope: SandboxEnvelope | None
    replay_envelope: ReplayEnvelope
    audit_log_event: Mapping[str, Any]
    governance_reports: Mapping[str, Mapping[str, Any]]
    downstream_disposition: tuple[str, ...]
    hard_stop: bool
    revalidate_required: bool
    re_clearance_required: bool

    def __post_init__(self) -> None:
        if self.decision == DecisionVerdict.CERTIFY:
            if self.capability_token is None or self.sandbox_envelope is None:
                raise ValueError(
                    "GovernanceResult: CERTIFY requires capability_token + sandbox_envelope",
                )
            if self.hard_stop:
                raise ValueError("GovernanceResult: CERTIFY cannot have hard_stop=True")
        if self.decision == DecisionVerdict.REJECT and not self.hard_stop:
            # REJECT does not always mean hard_stop (a soft reject can be re-tried),
            # but a hard_constraint_breach reason code MUST imply hard_stop.
            if ReasonCode.HARD_CONSTRAINT_BREACH in self.reason_codes:
                raise ValueError(
                    "GovernanceResult: REJECT with HARD_CONSTRAINT_BREACH requires hard_stop=True",
                )
        if self.decision == DecisionVerdict.REMEDIATE:
            if ReasonCode.HARD_CONSTRAINT_BREACH in self.reason_codes:
                raise ValueError(
                    "GovernanceResult: REMEDIATE forbidden when hard_constraint breached "
                    "(spec Decision Rail Invariants line 645)",
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_log_event": dict(self.audit_log_event),
            "capability_token": self.capability_token.to_dict() if self.capability_token else None,
            "compliance_hash": self.compliance_hash,
            "decision": self.decision.value,
            "downstream_disposition": _sorted_strings(self.downstream_disposition),
            "governance_reports": {k: dict(v) for k, v in self.governance_reports.items()},
            "hard_stop": self.hard_stop,
            "origin_trust": self.origin_trust.to_dict(),
            "re_clearance_required": self.re_clearance_required,
            "reason_codes": sorted(c.value for c in self.reason_codes),
            "replay_envelope": self.replay_envelope.to_dict(),
            "revalidate_required": self.revalidate_required,
            "review_request": self.review_request.to_dict(),
            "sandbox_envelope": self.sandbox_envelope.to_dict() if self.sandbox_envelope else None,
            "standards_fingerprint": self.standards_fingerprint.to_dict(),
            "triage": self.triage.to_dict(),
        }


__all__ = [
    "CapabilityTokenV5",
    "GovernanceResult",
    "GovernanceReviewRequest",
    "HITLDispositionPacket",
    "OriginTrustManifest",
    "ReplayEnvelope",
    "RuntimeRegressionReport",
    "SandboxEnvelope",
    "StandardsFingerprint",
    "TriageReport",
]
