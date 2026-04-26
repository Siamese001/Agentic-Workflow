"""Canonical runtime contract dataclasses (per docs/reference/99.3 and 99.4).

These types describe the contract chain enforced by the E2E proof harness. They
are NOT runtime authority — they are inert data carriers used by validators to
prove a run honored every handoff rule, every authority boundary, and every
trace requirement laid out in the 99-series specs.

Contract chain (99.3):
    ValidatedRequest
      -> L1PlanContract
      -> RouteContract
      -> FinalEvidenceContract            (when grounding required)
      -> PromptEnvelope                   (when model execution required)
      -> L3WorkflowContract / L3StepContract (when managed workflow required)
      -> L2ExecutionRequest
      -> SealedL2Artifact
      -> ExitReviewPacket
      -> X3DispositionReceipt
      -> CommitRequest                    (when durable mutation requested)
      -> UWGCommitReceipt                 (when durable commit accepted)
      -> RuntimeExhaustBundle             (after current run boundary, to L6)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums (route families, dispositions, support levels, etc.)
# ---------------------------------------------------------------------------


class RouteId(str, Enum):
    """Route families enumerated in 99.2 route coverage table."""

    R1A_EXACT_CACHE = "R1A_EXACT_CACHE"
    R1B_SEMANTIC_CACHE = "R1B_SEMANTIC_CACHE"
    R5_FALLBACK = "R5_FALLBACK"
    R3_SIMPLE_GROUNDED_READ = "R3_SIMPLE_GROUNDED_READ"
    R4_SINGLE_ACTION = "R4_SINGLE_ACTION"
    R3_PLUS_R4_SINGLE_STEP = "R3_PLUS_R4_SINGLE_STEP"
    R3R4_MANAGED_WORKFLOW = "R3R4_MANAGED_WORKFLOW"
    HITL_POSTURE = "HITL_POSTURE"
    UWG_COMMIT_PATH = "UWG_COMMIT_PATH"


class ExecutionForm(str, Enum):
    SINGLE_STEP = "SINGLE_STEP"
    MULTI_STEP = "MULTI_STEP"
    TERMINAL_RET = "TERMINAL_RET"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class XDisposition(str, Enum):
    """X3 disposition outcomes consumed from Exit (per 99.6/99.8)."""

    X3A_APPROVE = "X3A_APPROVE"
    X3B_RETURN_FOR_FIX = "X3B_RETURN_FOR_FIX"
    X3C_COMMIT_ELIGIBLE = "X3C_COMMIT_ELIGIBLE"
    X3D_REJECT = "X3D_REJECT"


class SupportLevel(str, Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    INFERENCE = "INFERENCE"
    UNSUPPORTED = "UNSUPPORTED"


class OutputAction(str, Enum):
    INCLUDE = "INCLUDE"
    CAVEAT = "CAVEAT"
    ABSTAIN = "ABSTAIN"
    REMOVE = "REMOVE"


class ProofStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    EXPLAINED_VARIANCE = "EXPLAINED_VARIANCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"


# ---------------------------------------------------------------------------
# Authority root — every contract must carry these per 99.3 handoff rules
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContractRoot:
    """Authority fields preserved across the full contract chain (99.3)."""

    request_id: str
    run_id: str
    trace_root: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    tenant_id: str = "default"
    session_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "replay_key": self.replay_key,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
        }


# ---------------------------------------------------------------------------
# Layer 0/1/U0 contracts
# ---------------------------------------------------------------------------


@dataclass
class ValidatedRequest:
    """U0 intake output — bound identity + envelope (99.1 step 1)."""

    contract_type: str = "ValidatedRequest"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    user_intent_text: str = ""
    declared_grounding_required: bool = False
    declared_durable_write_requested: bool = False
    declared_hitl_required: bool = False
    upstream_ref: str | None = None  # always None — U0 has no upstream
    digest: str = ""


@dataclass
class L1PlanContract:
    """L1 cognition output — plan with grounding + support targets (99.1 step 2)."""

    contract_type: str = "L1PlanContract"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    grounding_required: bool = False
    support_target: str = ""
    risk_tier: str = "LOW"
    upstream_ref: str = ""  # ValidatedRequest.digest
    digest: str = ""


@dataclass
class RouteContract:
    """L0 routing output — selects a route family (99.1 step 3, 99.2)."""

    contract_type: str = "RouteContract"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    route_id: RouteId = RouteId.R5_FALLBACK
    execution_form: ExecutionForm = ExecutionForm.SINGLE_STEP
    upstream_ref: str = ""  # L1PlanContract.digest
    route_digest: str = ""
    digest: str = ""


# ---------------------------------------------------------------------------
# C0 retrieval contracts — only emitted when grounding is required
# ---------------------------------------------------------------------------


@dataclass
class EvidenceRef:
    ref_id: str
    source_uri: str
    span_locator: str = ""
    content_hash: str = ""


@dataclass
class FinalEvidenceContract:
    """C0 emits this when grounding is required (99.1 step 4, 99.7)."""

    contract_type: str = "FinalEvidenceContract"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # RouteContract.digest
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    evidence_contract_hash: str = ""
    digest: str = ""


# ---------------------------------------------------------------------------
# Prompt assembly contract — emitted when model execution is required
# ---------------------------------------------------------------------------


@dataclass
class PromptEnvelope:
    """PA emits this when prompt assembly is required (99.1 step 5, 99.7)."""

    contract_type: str = "PromptEnvelope"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_evidence_ref: str = ""  # FinalEvidenceContract.digest, if any
    upstream_route_ref: str = ""  # RouteContract.digest
    bom_digest: str = ""
    prompt_hash: str = ""
    schema_bound: bool = False
    digest: str = ""


# ---------------------------------------------------------------------------
# L3 contracts — emitted only for managed workflows
# ---------------------------------------------------------------------------


@dataclass
class L3StepContract:
    step_id: str
    depends_on: list[str] = field(default_factory=list)
    digest: str = ""


@dataclass
class L3WorkflowContract:
    contract_type: str = "L3WorkflowContract"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # RouteContract.digest
    steps: list[L3StepContract] = field(default_factory=list)
    digest: str = ""


# ---------------------------------------------------------------------------
# L2 execution contracts
# ---------------------------------------------------------------------------


@dataclass
class L2ExecutionRequest:
    contract_type: str = "L2ExecutionRequest"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_route_ref: str = ""
    upstream_prompt_ref: str = ""
    digest: str = ""


@dataclass
class SealedL2Artifact:
    """L2 sealed output (99.1 step 6)."""

    contract_type: str = "SealedL2Artifact"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # L2ExecutionRequest.digest OR RouteContract.digest for terminal RET
    output_text: str = ""
    cited_evidence_refs: list[str] = field(default_factory=list)
    side_effect: bool = False
    direct_l4_write: bool = False  # MUST be False — only UWG writes L4
    digest: str = ""


# ---------------------------------------------------------------------------
# Exit / disposition / commit contracts
# ---------------------------------------------------------------------------


@dataclass
class ExitReviewPacket:
    """Exit normalize+evaluate output (99.1 step 7)."""

    contract_type: str = "ExitReviewPacket"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # SealedL2Artifact.digest
    terminal_classification: str = ""  # MUST be set; absence = fail
    gate_verdicts: list[dict[str, Any]] = field(default_factory=list)
    digest: str = ""


@dataclass
class X3DispositionReceipt:
    contract_type: str = "X3DispositionReceipt"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # ExitReviewPacket.digest
    disposition: XDisposition = XDisposition.X3A_APPROVE
    digest: str = ""


@dataclass
class CommitRequest:
    contract_type: str = "CommitRequest"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # X3DispositionReceipt.digest, MUST be X3C_COMMIT_ELIGIBLE
    state_diff: dict[str, Any] = field(default_factory=dict)
    digest: str = ""


@dataclass
class UWGCommitReceipt:
    contract_type: str = "UWGCommitReceipt"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # CommitRequest.digest
    accepted: bool = False
    l4_audit_append_id: str = ""
    digest: str = ""


# ---------------------------------------------------------------------------
# L6 exhaust — only emitted AFTER X3 disposition is sealed
# ---------------------------------------------------------------------------


@dataclass
class RuntimeExhaustBundle:
    contract_type: str = "RuntimeExhaustBundle"
    root: ContractRoot = field(default_factory=lambda: ContractRoot("", "", "", "", "", ""))
    upstream_ref: str = ""  # X3DispositionReceipt.digest, REQUIRED before L6 ingest
    spans_count: int = 0
    digest: str = ""


# ---------------------------------------------------------------------------
# OTEL span (99.4) and groundedness support map (99.7)
# ---------------------------------------------------------------------------


@dataclass
class OTELSpan:
    span_id: str
    parent_span_id: str | None
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    start_ns: int = 0
    end_ns: int = 0
    status: str = "OK"


@dataclass
class ClaimSupport:
    claim_id: str
    claim_text: str
    support_target_type: str
    supporting_evidence_refs: list[str]
    cited_span_refs: list[str]
    citation_anchor_status: str
    contradiction_refs: list[str]
    freshness_status: str
    authority_status: str
    support_level: SupportLevel
    output_action: OutputAction


# ---------------------------------------------------------------------------
# Receipts (99.5, 99.6, 99.7)
# ---------------------------------------------------------------------------


@dataclass
class ReplayComparisonReceipt:
    replay_id: str
    original_run_id: str
    replay_run_id: str
    replay_scope: list[str]
    input_digest_match: bool
    route_digest_match: bool
    evidence_digest_match: bool
    prompt_digest_match: bool
    execution_digest_match: bool
    exit_digest_match: bool
    commit_digest_match: bool | None
    nondeterminism_flags: list[str]
    accepted_variance: list[str]
    replay_status: ProofStatus


@dataclass
class NoBypassProofReceipt:
    scenario_id: str
    run_id: str
    trace_root: str
    checked_surfaces: list[str]
    prohibited_spans_absent: list[str]
    prohibited_write_paths_absent: list[str]
    authority_boundary_status: str
    violations: list[str]
    proof_status: ProofStatus


@dataclass
class GroundednessProofReceipt:
    final_response_id: str
    evidence_contract_id: str
    prompt_artifact_id: str
    claim_support_map: list[ClaimSupport]
    unsupported_claims: list[str]
    contradiction_handling_status: str
    prompt_data_boundary_status: str
    proof_status: ProofStatus


__all__ = [
    "RouteId",
    "ExecutionForm",
    "XDisposition",
    "SupportLevel",
    "OutputAction",
    "ProofStatus",
    "ContractRoot",
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "EvidenceRef",
    "FinalEvidenceContract",
    "PromptEnvelope",
    "L3StepContract",
    "L3WorkflowContract",
    "L2ExecutionRequest",
    "SealedL2Artifact",
    "ExitReviewPacket",
    "X3DispositionReceipt",
    "CommitRequest",
    "UWGCommitReceipt",
    "RuntimeExhaustBundle",
    "OTELSpan",
    "ClaimSupport",
    "ReplayComparisonReceipt",
    "NoBypassProofReceipt",
    "GroundednessProofReceipt",
]
