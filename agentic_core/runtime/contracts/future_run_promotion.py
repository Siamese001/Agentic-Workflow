"""Future run promotion contract — W10 extended shape.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

This module defines the W10-canonical FutureRunPromotionRequest with all
required fields as specified in the W10 acceptance criteria.  It is separate
from the legacy ``future_run_promotion_types.py`` which holds typed payload
sub-contracts (R1APromotionPayload etc.).

Invariants (non-negotiable):
  - current_run_mutation_allowed is always False.
  - requires_uwg is always True.
  - Only L6WritebackProposer creates these; UWG admits or blocks.
  - No durable writes occur by constructing this object.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Canonical promotion types for future-run proposals
# ---------------------------------------------------------------------------

PROMOTION_TYPE_EXACT_CACHE_WRITEBACK = "exact_cache_writeback"
PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK = "semantic_cache_writeback"
PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK = "evidence_artifact_writeback"
PROMOTION_TYPE_PROMPT_PROFILE_UPDATE = "prompt_profile_update"
PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE = "rubric_threshold_update"
PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE = "judge_calibration_update"
PROMOTION_TYPE_ROUTE_POLICY_UPDATE = "route_policy_update"
PROMOTION_TYPE_CACHE_POLICY_UPDATE = "cache_policy_update"
PROMOTION_TYPE_INDEX_REFRESH_REQUEST = "index_refresh_request"

KNOWN_PROMOTION_TYPES: frozenset[str] = frozenset({
    PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
    PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
    PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK,
    PROMOTION_TYPE_PROMPT_PROFILE_UPDATE,
    PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE,
    PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE,
    PROMOTION_TYPE_ROUTE_POLICY_UPDATE,
    PROMOTION_TYPE_CACHE_POLICY_UPDATE,
    PROMOTION_TYPE_INDEX_REFRESH_REQUEST,
})

# Target stores
TARGET_STORE_EXACT_CACHE = "r1a_exact_cache"
TARGET_STORE_SEMANTIC_CACHE = "r1b_semantic_cache"
TARGET_STORE_EVIDENCE_STORE = "c0_evidence_store"
TARGET_STORE_PROMPT_REGISTRY = "prompt_profile_registry"
TARGET_STORE_RUBRIC_REGISTRY = "rubric_threshold_registry"
TARGET_STORE_JUDGE_CALIBRATION = "judge_calibration_store"
TARGET_STORE_ROUTE_POLICY = "route_policy_registry"
TARGET_STORE_CACHE_POLICY = "cache_policy_registry"
TARGET_STORE_VECTOR_INDEX = "vector_index"

# Safety classes
SAFETY_CLASS_STANDARD = "standard"
SAFETY_CLASS_ELEVATED = "elevated"
SAFETY_CLASS_RESTRICTED = "restricted"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return "sha256::" + hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class FutureRunPromotionRequest:
    """W10 canonical inert post-runtime promotion proposal.

    Created by L6WritebackProposer ONLY after RuntimeExhaustBundle confirms
    the current run is closed.  Has no authority — UWG admits or blocks.

    ``current_run_mutation_allowed`` and ``requires_uwg`` are structurally
    enforced: construction raises if they deviate from their invariant values.
    """

    promotion_request_id: str = ""
    source_runtime_exhaust_bundle_ref: str = ""  # RuntimeExhaustBundle.bundle_id

    app_id: str = ""
    task_class: str = ""
    promotion_type: str = ""    # one of PROMOTION_TYPE_* constants
    target_store: str = ""      # one of TARGET_STORE_* constants
    target_ref: str = ""        # specific key/ref in target_store

    proposed_state_diff: str = ""   # JSON-serialised diff (inert until UWG admits)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    metric_summary: str = ""        # JSON-serialised metric snapshot

    confidence: float = 0.0
    safety_class: str = SAFETY_CLASS_STANDARD
    policy_ref: str = ""
    learning_profile_ref: str = ""
    meta_feedback_profile_ref: str = ""
    completed_eval_record_ref: str = ""
    rca_packet_ref: str = ""
    audit_manifest_ref: str = ""
    l6_gate_receipt_refs: tuple[str, ...] = field(default_factory=tuple)

    # Structural invariants — MUST NOT be changed
    current_run_mutation_allowed: bool = False   # always False
    requires_uwg: bool = True                    # always True

    created_at: str = ""
    deterministic_digest: str = ""

    schema_version: str = "w10.1"

    def __post_init__(self) -> None:
        if self.current_run_mutation_allowed is not False:
            raise ValueError(
                "FutureRunPromotionRequest: current_run_mutation_allowed must be False. "
                "Promotion requests must never mutate the current run."
            )
        if self.requires_uwg is not True:
            raise ValueError(
                "FutureRunPromotionRequest: requires_uwg must be True. "
                "All durable writes must go through UWG."
            )
        if not self.policy_ref:
            raise ValueError(
                "FutureRunPromotionRequest: policy_ref is required. "
                "Every promotion request must reference a policy."
            )
        if not self.evidence_refs:
            raise ValueError(
                "FutureRunPromotionRequest: evidence_refs must be non-empty. "
                "Promotion without evidence is not allowed."
            )

    def as_dict(self) -> dict:
        return {
            "promotion_request_id": self.promotion_request_id,
            "source_runtime_exhaust_bundle_ref": self.source_runtime_exhaust_bundle_ref,
            "app_id": self.app_id,
            "task_class": self.task_class,
            "promotion_type": self.promotion_type,
            "target_store": self.target_store,
            "target_ref": self.target_ref,
            "proposed_state_diff": self.proposed_state_diff,
            "evidence_refs": list(self.evidence_refs),
            "metric_summary": self.metric_summary,
            "confidence": self.confidence,
            "safety_class": self.safety_class,
            "policy_ref": self.policy_ref,
            "learning_profile_ref": self.learning_profile_ref,
            "meta_feedback_profile_ref": self.meta_feedback_profile_ref,
            "completed_eval_record_ref": self.completed_eval_record_ref,
            "rca_packet_ref": self.rca_packet_ref,
            "audit_manifest_ref": self.audit_manifest_ref,
            "l6_gate_receipt_refs": list(self.l6_gate_receipt_refs),
            "current_run_mutation_allowed": self.current_run_mutation_allowed,
            "requires_uwg": self.requires_uwg,
            "created_at": self.created_at,
            "deterministic_digest": self.deterministic_digest,
            "schema_version": self.schema_version,
        }


def build_future_run_promotion_request(
    *,
    source_bundle_ref: str,
    app_id: str,
    task_class: str,
    promotion_type: str,
    target_store: str,
    target_ref: str,
    evidence_refs: tuple[str, ...],
    policy_ref: str,
    proposed_state_diff: str = "{}",
    metric_summary: str = "{}",
    confidence: float = 0.0,
    safety_class: str = SAFETY_CLASS_STANDARD,
    learning_profile_ref: str = "",
    meta_feedback_profile_ref: str = "",
    completed_eval_record_ref: str = "",
    rca_packet_ref: str = "",
    audit_manifest_ref: str = "",
    l6_gate_receipt_refs: tuple[str, ...] = (),
    legacy_writeback_override: bool = False,
) -> FutureRunPromotionRequest:
    """Factory — builds an inert FutureRunPromotionRequest for UWG admission."""
    if not legacy_writeback_override and not (
        completed_eval_record_ref and rca_packet_ref and audit_manifest_ref
    ):
        raise ValueError(
            "build_future_run_promotion_request requires completed_eval_record_ref, "
            "rca_packet_ref, and audit_manifest_ref unless legacy_writeback_override=True"
        )
    promotion_request_id = f"promo::{app_id}::{promotion_type}::{uuid.uuid4().hex[:8]}"
    created_at = _utcnow()

    core: dict = {
        "promotion_request_id": promotion_request_id,
        "source_runtime_exhaust_bundle_ref": source_bundle_ref,
        "app_id": app_id,
        "task_class": task_class,
        "promotion_type": promotion_type,
        "target_store": target_store,
        "target_ref": target_ref,
        "policy_ref": policy_ref,
        "confidence": confidence,
        "created_at": created_at,
    }
    digest = _digest(core)

    return FutureRunPromotionRequest(
        promotion_request_id=promotion_request_id,
        source_runtime_exhaust_bundle_ref=source_bundle_ref,
        app_id=app_id,
        task_class=task_class,
        promotion_type=promotion_type,
        target_store=target_store,
        target_ref=target_ref,
        proposed_state_diff=proposed_state_diff,
        evidence_refs=evidence_refs,
        metric_summary=metric_summary,
        confidence=confidence,
        safety_class=safety_class,
        policy_ref=policy_ref,
        learning_profile_ref=learning_profile_ref,
        meta_feedback_profile_ref=meta_feedback_profile_ref,
        completed_eval_record_ref=completed_eval_record_ref,
        rca_packet_ref=rca_packet_ref,
        audit_manifest_ref=audit_manifest_ref,
        l6_gate_receipt_refs=l6_gate_receipt_refs,
        current_run_mutation_allowed=False,
        requires_uwg=True,
        created_at=created_at,
        deterministic_digest=digest,
    )


__all__ = [
    "FutureRunPromotionRequest",
    "build_future_run_promotion_request",
    "PROMOTION_TYPE_EXACT_CACHE_WRITEBACK",
    "PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK",
    "PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK",
    "PROMOTION_TYPE_PROMPT_PROFILE_UPDATE",
    "PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE",
    "PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE",
    "PROMOTION_TYPE_ROUTE_POLICY_UPDATE",
    "PROMOTION_TYPE_CACHE_POLICY_UPDATE",
    "PROMOTION_TYPE_INDEX_REFRESH_REQUEST",
    "KNOWN_PROMOTION_TYPES",
    "TARGET_STORE_EXACT_CACHE",
    "TARGET_STORE_SEMANTIC_CACHE",
    "TARGET_STORE_EVIDENCE_STORE",
    "TARGET_STORE_PROMPT_REGISTRY",
    "TARGET_STORE_RUBRIC_REGISTRY",
    "TARGET_STORE_JUDGE_CALIBRATION",
    "TARGET_STORE_ROUTE_POLICY",
    "TARGET_STORE_CACHE_POLICY",
    "TARGET_STORE_VECTOR_INDEX",
    "SAFETY_CLASS_STANDARD",
    "SAFETY_CLASS_ELEVATED",
    "SAFETY_CLASS_RESTRICTED",
]
