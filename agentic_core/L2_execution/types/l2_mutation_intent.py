"""L2 StateDiff Candidate & Mutation Intent Contracts (spec 04.9).

Defines the only mutation-shaped output L2 is allowed to produce: an inert
proposed_state_diff_candidate sealed into a StateDiffCandidateManifest. L2
never writes it. Exit may evaluate, UWG may validate, L4 may store.

Source spec: docs/reference/04_L2_Execute/04.9_L2_StateDiffCandidate_and_Mutation_Intent.md

Invariants enforced here:
    - ProposedStateDiffCandidate.inert_until_exit_uwg is forced True.
    - ProposedStateDiffCandidate.write_auth_status == 'none_inside_l2'.
    - StateDiffCandidateManifest.l2_no_commit_assertion must be True.
    - FORBIDDEN: modifying candidate after E5 seal (immutable dataclass).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MutationSourceStage(str, Enum):
    E3_EXEC = "E3_EXEC"
    E4_HEAL = "E4_HEAL"
    E5_SEAL = "E5_SEAL"


class MutationIntentClass(str, Enum):
    NONE = "none"
    SANDBOX_ARTIFACT = "sandbox_artifact"
    EXTERNAL_ACTION_RESULT = "external_action_result"
    L4_STATE_CANDIDATE = "l4_state_candidate"
    CACHE_CANDIDATE = "cache_candidate"
    MEMORY_CANDIDATE = "memory_candidate"
    POLICY_CANDIDATE = "policy_candidate"
    REGISTRY_CANDIDATE = "registry_candidate"


class CandidateKind(str, Enum):
    JSON_PATCH = "json_patch"
    SEMANTIC_DIFF = "semantic_diff"
    ARTIFACT_PUBLICATION = "artifact_publication"
    MEMORY_PROMOTION_CANDIDATE = "memory_promotion_candidate"
    CACHE_CANDIDATE = "cache_candidate"
    REGISTRY_CANDIDATE = "registry_candidate"
    POLICY_CANDIDATE = "policy_candidate"
    ROLLBACK_CANDIDATE = "rollback_candidate"


class SchemaValidationStatus(str, Enum):
    LOCALLY_VALID = "locally_valid"
    LOCALLY_INVALID = "locally_invalid"
    NOT_VALIDATED = "not_validated"


# Constrained literal values per spec 04.9.
WRITE_AUTH_NONE_INSIDE_L2 = "none_inside_l2"


@dataclass(frozen=True)
class MutationIntentDetectionReceipt:
    """Receipt emitted whenever L2 detects mutation-shaped output from E3/E4/E5."""

    detection_receipt_id: str
    request_id: str
    run_id: str
    trace_root: str
    source_stage: MutationSourceStage
    mutation_detected: bool
    mutation_intent_class: MutationIntentClass
    side_effect_class: str
    irreversible_risk: bool
    high_impact_risk: bool
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    deterministic_digest: str
    reason_codes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.detection_receipt_id:
            raise ValueError("detection_receipt_id required")
        if self.mutation_detected and self.mutation_intent_class is MutationIntentClass.NONE:
            raise ValueError(
                "mutation_detected=True but mutation_intent_class=NONE is inconsistent"
            )
        if not self.mutation_detected and self.mutation_intent_class is not MutationIntentClass.NONE:
            raise ValueError(
                "mutation_detected=False requires mutation_intent_class=NONE"
            )
        for required in ("policy_hash", "blueprint_hash", "replay_key", "deterministic_digest"):
            if not getattr(self, required):
                raise ValueError(f"MutationIntentDetectionReceipt.{required} required")


@dataclass(frozen=True)
class ProposedStateDiffCandidate:
    """Inert mutation candidate. L2 never commits this — Exit/UWG may later."""

    candidate_id: str
    candidate_kind: CandidateKind
    target_surface_hint: str
    target_object_ref: str
    after_candidate_ref: str
    diff_payload_ref: str
    diff_payload_hash: str
    schema_ref: str
    schema_validation_status: SchemaValidationStatus
    route_contract_ref: str
    l2_authority_ref: str
    capability_token_ref: str
    sandbox_envelope_ref: str
    blast_radius_hint: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    trace_root: str
    deterministic_digest: str
    before_ref: Optional[str] = None
    rollback_hint_ref: Optional[str] = None
    evidence_refs: tuple[str, ...] = ()
    # Invariant constants per spec 04.9 — do not override.
    write_auth_status: str = WRITE_AUTH_NONE_INSIDE_L2
    inert_until_exit_uwg: bool = True

    def __post_init__(self) -> None:
        if self.write_auth_status != WRITE_AUTH_NONE_INSIDE_L2:
            raise ValueError(
                "ProposedStateDiffCandidate.write_auth_status must be "
                f"'{WRITE_AUTH_NONE_INSIDE_L2}' (spec 04.9)"
            )
        if not self.inert_until_exit_uwg:
            raise ValueError(
                "ProposedStateDiffCandidate.inert_until_exit_uwg must be True (spec 04.9)"
            )
        for required in (
            "candidate_id",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "route_contract_ref",
            "capability_token_ref",
            "sandbox_envelope_ref",
            "diff_payload_hash",
            "deterministic_digest",
        ):
            if not getattr(self, required):
                raise ValueError(f"ProposedStateDiffCandidate.{required} required")


@dataclass(frozen=True)
class StateDiffCandidateManifest:
    """E5 Seal includes this if any candidate exists."""

    manifest_id: str
    candidate_count: int
    total_payload_hash: str
    local_validation_summary: str
    forbidden_direct_write_check: bool
    exit_handoff_eligibility_hint: str
    sealed_l2_artifact_ref: str
    proposed_state_diff_candidate_refs: tuple[str, ...] = ()
    # Invariant constant — L2 never commits.
    l2_no_commit_assertion: bool = True

    def __post_init__(self) -> None:
        if not self.l2_no_commit_assertion:
            raise ValueError(
                "StateDiffCandidateManifest.l2_no_commit_assertion must be True (spec 04.9)"
            )
        if not self.forbidden_direct_write_check:
            raise ValueError(
                "StateDiffCandidateManifest.forbidden_direct_write_check must be True"
            )
        if self.candidate_count != len(self.proposed_state_diff_candidate_refs):
            raise ValueError(
                "candidate_count must equal len(proposed_state_diff_candidate_refs)"
            )
        if not self.manifest_id or not self.sealed_l2_artifact_ref:
            raise ValueError("manifest_id and sealed_l2_artifact_ref required")


__all__ = [
    "CandidateKind",
    "MutationIntentClass",
    "MutationIntentDetectionReceipt",
    "MutationSourceStage",
    "ProposedStateDiffCandidate",
    "SchemaValidationStatus",
    "StateDiffCandidateManifest",
    "WRITE_AUTH_NONE_INSIDE_L2",
]
