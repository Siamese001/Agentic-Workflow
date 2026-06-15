"""L6 Learning — Package-Driven Completed-Run Evaluation & Future-Run Promotion

W10 Implementation: Post-runtime learning that emits inert proposals for future runs.

Core Principle: L6 is POST-RUNTIME ONLY
- Cannot rescue, mutate, reroute, re-execute current run
- Cannot write L4, cache, or vector store directly
- Can only emit inert proposals that go to UWG for review
- Activation only at future run_start with rollback plan

Hard Rules:
1. L6 never touches current-run execution
2. L6 never emits X3
3. L6 never writes cache/vector store/L4 directly
4. All proposals are inert until UWG approval
5. Promotion requires replay/regression/safety proof

Relocated from ``agentic_core/L6_learning/`` into the canonical active-L6 surface
(chapter 06.7 — Gauntlet → Approval → UWG Promotion → Future Run) per ADR-105. The
legacy ``agentic_core.L6_learning`` path is a deprecated compat shim (sunset 2026-06-29).
"""
__layer__ = "L6"
__l6_surface__ = "active"
__l6_chapter__ = "06.7"

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto


class ProposalType(Enum):
    """Types of inert future-run proposals."""
    CACHE_THRESHOLD = auto()
    SOURCE_RELIABILITY = auto()
    ENTITY_ALIAS = auto()
    JUDGE_CALIBRATION = auto()
    RETRIEVAL_PROFILE = auto()
    FRESHNESS_TTL = auto()
    CHUNKING_PROFILE = auto()
    PROMPT_IMPROVEMENT = auto()
    RUBRIC_IMPROVEMENT = auto()


class ProofType(Enum):
    """Required proof types for promotion."""
    REPLAY = auto()
    REGRESSION = auto()
    SAFETY = auto()
    CALIBRATION = auto()


@dataclass(frozen=True)
class CompletedEvalRecord:
    """Immutable record of completed run evaluation.
    
    Emitted after runtime boundary. Cannot modify current run.
    """
    run_id: str
    trace_root: str
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Inputs consumed (read-only references)
    runtime_exhaust_bundle_ref: str = ""
    exit_disposition_receipt_ref: str = ""
    gate_mesh_result_ref: str = ""
    x1_checkout_result_ref: str = ""
    x2_aggregation_result_ref: str = ""
    sealed_l2_artifact_ref: str = ""
    final_evidence_contract_ref: str = ""
    judge_evidence_refs: Tuple[str, ...] = ()
    
    # Learning observations (inert, no current-run mutation)
    entity_alias_observations: Dict[str, Any] = field(default_factory=dict)
    source_reliability_signals: Dict[str, Any] = field(default_factory=dict)
    retrieval_profile_tuning_hints: Dict[str, Any] = field(default_factory=dict)
    cache_threshold_proposals: Dict[str, Any] = field(default_factory=dict)
    freshness_ttl_proposals: Dict[str, Any] = field(default_factory=dict)
    chunking_profile_hints: Dict[str, Any] = field(default_factory=dict)
    judge_calibration_signals: Dict[str, Any] = field(default_factory=dict)
    prompt_rubric_candidates: Dict[str, Any] = field(default_factory=dict)
    downstream_usefulness_signals: Dict[str, Any] = field(default_factory=dict)
    
    # Evidence digest
    evidence_digest: str = ""
    
    def __post_init__(self) -> None:
        """Verify immutability constraints."""
        # Ensure no current-run mutation paths
        object.__setattr__(self, '_frozen', True)


@dataclass(frozen=True)
class RCAPacket:
    """Root Cause Analysis packet for completed run.
    
    Inert analysis. No current-run repair.
    """
    run_id: str
    rca_id: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Analysis (observational only)
    gate_failure_patterns: List[Dict[str, Any]] = field(default_factory=list)
    judge_disagreement_patterns: List[Dict[str, Any]] = field(default_factory=list)
    cache_hit_anomaly_patterns: List[Dict[str, Any]] = field(default_factory=list)
    source_quality_deficits: List[Dict[str, Any]] = field(default_factory=list)
    
    # Root cause hypotheses (not repairs)
    root_cause_hypotheses: List[str] = field(default_factory=list)
    contributing_factors: List[str] = field(default_factory=list)
    
    # Evidence refs (read-only)
    evidence_refs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ProposalPacket:
    """Inert future-run proposal packet.
    
    Requires UWG review before activation.
    """
    proposal_id: str
    run_id: str
    proposal_type: ProposalType
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Proposal content (inert until UWG)
    target_dimension: str = ""
    proposed_change: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    confidence: float = 0.0
    
    # Required proofs (must be provided before promotion)
    required_proofs: Tuple[ProofType, ...] = ()
    proof_refs: Dict[str, str] = field(default_factory=dict)
    
    # Safety constraints
    rollback_plan_ref: str = ""  # Required for activation
    safety_review_status: str = "PENDING_UWG"
    
    # Future-run only
    activation_trigger: str = "FUTURE_RUN_START"  # Never current run
    
    def is_inert(self) -> bool:
        """Check if proposal is still inert (not activated)."""
        return self.safety_review_status != "ACTIVATED"


@dataclass(frozen=True)
class FutureRunPromotionRequest:
    """Request for promoting learning to future runs.
    
    Inert until all proofs provided and UWG approves.
    """
    request_id: str
    run_id: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Proposals bundled
    proposal_packets: Tuple[ProposalPacket, ...] = ()
    
    # Proof requirements
    replay_proof_ref: str = ""  # Demonstrates fix works
    regression_proof_ref: str = ""  # Demonstrates no regression
    safety_proof_ref: str = ""  # Safety review passed
    calibration_proof_ref: str = ""  # Judge calibration verified (pre-existing; not re-added)

    # W1 proof fields (required before promotion; default "" for backward compat)
    audit_manifest_ref: str = ""       # Required for every promotion request (no exceptions)
    completed_eval_record_ref: str = ""  # Required for every L6 future-run promotion
    rca_packet_ref: str = ""           # Required for corrective/policy/prompt/rubric/judge/cache changes

    # Rollback plan (required)
    rollback_plan_ref: str = ""
    
    # Activation constraints
    target_future_run_window: str = "NEXT_RUN"  # Or specific date range
    auto_activate: bool = False  # Never auto-activate without UWG
    
    # UWG review status
    uwg_review_status: str = "PENDING"
    uwg_approval_ref: str = ""


@dataclass(frozen=True)
class L6GauntletResult:
    """Result of L6 gauntlet (validation gate).

    gate_id identifies which gate produced this result (e.g. 'G29').
    It is a ledger-tracking identifier ONLY — it does NOT constitute
    GateVerdict evidence, 00C proof, Exit certification, UWG admission,
    or L5 certification. Presence of gate_id never implies passed=True.
    """
    run_id: str
    passed: bool
    failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    evidence_digest: str = ""
    gate_id: str = ""  # Populated from PromotionGauntlet.GATE_ID; identifier only


@dataclass(frozen=True)
class ObserverLawReceipt:
    """Receipt confirming L6 observer law compliance.
    
    Certifies L6 did not violate current-run boundary.
    """
    run_id: str
    l6_session_id: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Compliance assertions
    no_current_run_mutation: bool = True
    no_x3_emission: bool = True
    no_cache_write: bool = True
    no_vector_store_write: bool = True
    no_l4_write: bool = True
    no_reroute_attempt: bool = True
    no_reexecute_attempt: bool = True
    
    # Evidence
    compliance_digest: str = ""
    evidence_refs: Tuple[str, ...] = ()


# Re-export for convenience
__all__ = [
    "ProposalType",
    "ProofType", 
    "CompletedEvalRecord",
    "RCAPacket",
    "ProposalPacket",
    "FutureRunPromotionRequest",
    "L6GauntletResult",
    "ObserverLawReceipt",
    "PromotionGauntlet",
]

# Lazy-imported to avoid circular dependency; exported at package level for
# downstream consumers that do `from agentic_core.L6_system_learning.future_run_promotion import PromotionGauntlet`
from agentic_core.L6_system_learning.future_run_promotion.promotion_gauntlet import PromotionGauntlet as PromotionGauntlet  # noqa: E402
