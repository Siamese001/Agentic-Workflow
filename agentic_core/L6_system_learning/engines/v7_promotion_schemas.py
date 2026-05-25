"""V7 canonical schemas — PromotionPacket + FailureMode taxonomy.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
- ``PromotionPacket`` schema: lines 1369-1414 (45 fields)
- ``FailureMode`` containment table: lines 1344-1362 (15 modes)

These are pure dataclasses — no I/O, no business logic. Every field name
matches the spec exactly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


# =====================================================================
# PromotionPacket schema (spec lines 1369-1414)
# =====================================================================


@dataclass(frozen=True)
class EvidenceLink:
    """One row of ``evidence_links[]`` (spec lines 1389-1395)."""

    trace_id: str
    span_id: str
    run_id: str
    replay_key: str
    artifact_hash: str
    source_id: str
    cited_span: str | None = None


@dataclass(frozen=True)
class ActivationPolicySpec:
    """``activation_policy`` block (spec lines 1406-1410)."""

    future_run_only: bool  # MUST be True
    activate_at: str  # always "next_run_start"
    canary_scope: str | None
    ttl_review_date_epoch: float


@dataclass(frozen=True)
class PromotionPacket:
    """Canonical v7 promotion packet — every field from spec lines 1369-1414.

    The packet is immutable. UWG Master Clerk consumes a fully-constructed
    instance; partial packets MUST be rejected upstream by S3E proposal
    admission.
    """

    # Identity / lineage
    proposal_id: str
    proposal_type: str
    target_surface: str
    target_version_current: str
    target_version_proposed: str
    proposed_diff: str
    content_hash: str
    signer_identity: str
    owner: str
    policy_hash: str

    # Evaluation references
    eval_record_id: str
    outcome_eval_ref: str
    trajectory_eval_ref: str
    governance_eval_ref: str
    calibration_ref: str | None  # optional — only required if SME-class change

    # RCA references
    rca_packet_id: str
    incident_ids: tuple[str, ...]
    pattern_ids: tuple[str, ...]

    # Evidence
    evidence_links: tuple[EvidenceLink, ...]
    root_cause_class: str
    first_bad_span: str | None

    # Effect / scope
    expected_effect: str
    affected_surfaces: tuple[str, ...]
    blast_radius: str
    regression_pack_ids: tuple[str, ...]
    golden_set_ids: tuple[str, ...]

    # Gauntlet + rollout
    gauntlet_receipt: str
    rollout_plan: str
    rollback_plan: str
    activation_policy: ActivationPolicySpec

    # Approval + ledger
    approval_decision_id: str
    uwg_receipt_id: str
    l4_version_digest: str
    bus_u_activation_receipt: str

    # Optional metadata
    extra_metadata: Mapping[str, str] = field(default_factory=dict)


def validate_promotion_packet(packet: PromotionPacket) -> tuple[str, ...]:
    """Validate spec invariants on a constructed packet.

    Returns a tuple of error strings (empty tuple = valid). Checks:

    - ``activation_policy.future_run_only is True`` (invariant 9, line 1290)
    - ``activation_policy.activate_at == "next_run_start"`` (line 1408)
    - ``content_hash`` non-empty (invariant 6, line 1276)
    - ``rollback_plan`` non-empty (invariant 12, line 1306)
    - ``signer_identity`` non-empty (invariant 6)
    - ``policy_hash`` non-empty (invariant 6)
    - ``rca_packet_id`` non-empty (invariant 5)
    - ``eval_record_id`` non-empty (invariant 2)
    - ``evidence_links`` not empty (invariant 11, line 1303)
    """
    errors: list[str] = []

    if not packet.activation_policy.future_run_only:
        errors.append(
            "INV9_FUTURE_RUN_ONLY_VIOLATED: future_run_only must be True"
        )
    if packet.activation_policy.activate_at != "next_run_start":
        errors.append(
            f"INV9_ACTIVATE_AT_VIOLATED: activate_at must be 'next_run_start', "
            f"got {packet.activation_policy.activate_at!r}"
        )
    if not packet.content_hash:
        errors.append("INV6_NO_SILENT_PROMOTE: content_hash is empty")
    if not packet.rollback_plan:
        errors.append("INV12_ROLLBACK_REQUIRED: rollback_plan is empty")
    if not packet.signer_identity:
        errors.append("INV6_NO_SILENT_PROMOTE: signer_identity is empty")
    if not packet.policy_hash:
        errors.append("INV6_NO_SILENT_PROMOTE: policy_hash is empty")
    if not packet.rca_packet_id:
        errors.append("INV5_RCA_REQUIRED: rca_packet_id is empty")
    if not packet.eval_record_id:
        errors.append("INV2_EVAL_BEFORE_LEARNING: eval_record_id is empty")
    if not packet.evidence_links:
        errors.append("INV11_LINEAGE_REQUIRED: evidence_links is empty")

    return tuple(errors)


# =====================================================================
# Failure-Mode containment taxonomy (spec lines 1344-1362)
# =====================================================================


class FailureMode(str, Enum):
    """15 v7 failure modes."""

    STALE_INGEST = "stale_ingest"
    ORPHAN_EVIDENCE = "orphan_evidence"
    EVAL_GAP = "eval_gap"
    FORCED_CERTAINTY = "forced_certainty"
    PREFERENCE_OVERFITTING = "preference_overfitting"
    RCA_VAGUENESS = "rca_vagueness"
    FALSE_PROMOTE = "false_promote"
    SHADOW_WRITER = "shadow_writer"
    STALE_EVAL_ON_WRITE = "stale_eval_on_write"
    PARTIAL_BYPASS = "partial_bypass"
    CURRENT_RUN_MUTATION = "current_run_mutation"
    ROLLBACK_MISSING = "rollback_missing"
    CACHE_CONTAMINATION = "cache_contamination"
    RUBRIC_DRIFT = "rubric_drift"
    REPLAY_NONLOCALIZATION = "replay_nonlocalization"


@dataclass(frozen=True)
class ContainmentAction:
    """Spec-defined containment for one ``FailureMode``."""

    mode: FailureMode
    looks_like: str
    containment: str


CONTAINMENT_TABLE: Mapping[FailureMode, ContainmentAction] = {
    FailureMode.STALE_INGEST: ContainmentAction(
        FailureMode.STALE_INGEST,
        "traces arrive late",
        "mark stale, block learning until refreshed",
    ),
    FailureMode.ORPHAN_EVIDENCE: ContainmentAction(
        FailureMode.ORPHAN_EVIDENCE,
        "artifact lacks trace/run link",
        "hold, request telemetry repair",
    ),
    FailureMode.EVAL_GAP: ContainmentAction(
        FailureMode.EVAL_GAP,
        "run has no completed eval",
        "block 6C/6D",
    ),
    FailureMode.FORCED_CERTAINTY: ContainmentAction(
        FailureMode.FORCED_CERTAINTY,
        "judge refuses Unknown",
        "calibration failure, block rubric",
    ),
    FailureMode.PREFERENCE_OVERFITTING: ContainmentAction(
        FailureMode.PREFERENCE_OVERFITTING,
        "likes/dislikes become policy",
        "require rubric + SME calibration",
    ),
    FailureMode.RCA_VAGUENESS: ContainmentAction(
        FailureMode.RCA_VAGUENESS,
        "'model bad' with no surface",
        "hold proposal",
    ),
    FailureMode.FALSE_PROMOTE: ContainmentAction(
        FailureMode.FALSE_PROMOTE,
        "gauntlet passes unsafe change",
        "rollback, mark gauntlet regression",
    ),
    FailureMode.SHADOW_WRITER: ContainmentAction(
        FailureMode.SHADOW_WRITER,
        "non-UWG mutation detected",
        "freeze, sovereignty incident",
    ),
    FailureMode.STALE_EVAL_ON_WRITE: ContainmentAction(
        FailureMode.STALE_EVAL_ON_WRITE,
        "old eval used for new commit",
        "UWG reject",
    ),
    FailureMode.PARTIAL_BYPASS: ContainmentAction(
        FailureMode.PARTIAL_BYPASS,
        "one failed stage ignored",
        "reject unless ADR exception",
    ),
    FailureMode.CURRENT_RUN_MUTATION: ContainmentAction(
        FailureMode.CURRENT_RUN_MUTATION,
        "learning changes live behavior",
        "fatal invariant breach",
    ),
    FailureMode.ROLLBACK_MISSING: ContainmentAction(
        FailureMode.ROLLBACK_MISSING,
        "promoted update cannot be reverted",
        "reject promotion",
    ),
    FailureMode.CACHE_CONTAMINATION: ContainmentAction(
        FailureMode.CACHE_CONTAMINATION,
        "bad exemplar/cache reused broadly",
        "disable surface, purge cache, RCA",
    ),
    FailureMode.RUBRIC_DRIFT: ContainmentAction(
        FailureMode.RUBRIC_DRIFT,
        "grader changes without calibration",
        "hold evals, recalibrate",
    ),
    FailureMode.REPLAY_NONLOCALIZATION: ContainmentAction(
        FailureMode.REPLAY_NONLOCALIZATION,
        "replay fails but cannot isolate span",
        "block promotion, improve instrumentation",
    ),
}


__all__ = [
    "EvidenceLink",
    "ActivationPolicySpec",
    "PromotionPacket",
    "validate_promotion_packet",
    "FailureMode",
    "ContainmentAction",
    "CONTAINMENT_TABLE",
]
