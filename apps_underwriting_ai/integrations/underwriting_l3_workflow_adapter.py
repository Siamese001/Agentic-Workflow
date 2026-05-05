"""L3 managed workflow adapter for apps_underwriting_ai.

Declares the five-stage workflow contract for R3R4_MANAGED_WORKFLOW.
L3 is responsible for EXPANDING the workflow (declaring the stage graph
with dependency edges, HITL posture, and evidence_refs enforcement rules).
L3 does NOT execute stages — execution is delegated to L2 step adapters
(underwriting_l2_step_adapters.py).

Five stages (linear dependency chain):
  Stage 1 — EvidenceRegisterEngine      → L2.E1.underwriting_execution_context_bound
  Stage 2 — DocumentReconciliationEngine → L2.E2.underwriting_evidence_validated
               (requires evidence_refs from FinalEvidenceContract)
  Stage 3 — FeatureDerivationEngine      → L2.E3.underwriting_stage_executed
               (requires evidence_refs from Stage 2 output)
  Stage 4 — RiskEvidenceScoringEngine    → L2.E3.underwriting_stage_executed
               (requires evidence_refs from Stage 3 output)
  Stage 5 — DecisionPacketAssembler      → L2.E5.underwriting_artifact_sealed
               (requires evidence_refs from Stage 4 output)

HITL posture is injected per run_context at expand time:
  - borderline_score_band: score in [0.40, 0.55) triggers HITL
  - contradiction_flags present: triggers HITL
  - c0_state FAIL: triggers HITL (adverse with weak evidence)
  - required_document_missing: triggers HITL (partial evidence adverse)

Conditional branches:
  - c0_state FAIL + no required docs → Stage 2 short-circuits to DEGRADE
  - contradiction_flags → Stage 5 injects CAVEAT_ENRICHMENT before sealing

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W3.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

WORKFLOW_ID = "underwriting_decision_packet_v1"
ROUTE_FAMILY = "R3R4_MANAGED_WORKFLOW"
STAGE_COUNT = 5

# Canonical L2 receipt type identifiers (referenced in stage contracts).
L2_RECEIPT_E1 = "L2.E1.underwriting_execution_context_bound"
L2_RECEIPT_E2 = "L2.E2.underwriting_evidence_validated"
L2_RECEIPT_E3 = "L2.E3.underwriting_stage_executed"
L2_RECEIPT_E5 = "L2.E5.underwriting_artifact_sealed"

# HITL posture values.
HITL_REQUIRED = "HITL_REQUIRED"
HITL_ADVISORY = "HITL_ADVISORY"
HITL_NONE = "HITL_NONE"

# Score thresholds for HITL posture injection.
HITL_SCORE_FLOOR = 0.40
HITL_SCORE_CEILING = 0.55

# Canonical stage contract templates — dependency edges declared here.
STAGE_CONTRACTS: list[dict[str, Any]] = [
    {
        "stage_id": "stage_1_evidence_register",
        "sequence": 1,
        "engine": "EvidenceRegisterEngine",
        "l2_receipt": L2_RECEIPT_E1,
        "output_type": "EvidenceRegister",
        "requires_evidence_refs": False,
        "depends_on": [],
        "conditional_branch": None,
        "hitl_trigger": None,
        "description": "Bind execution context; initialize EvidenceRegister from FinalEvidenceContract.",
    },
    {
        "stage_id": "stage_2_document_reconciliation",
        "sequence": 2,
        "engine": "DocumentReconciliationEngine",
        "l2_receipt": L2_RECEIPT_E2,
        "output_type": "ReconciliationResult",
        "requires_evidence_refs": True,
        "depends_on": ["stage_1_evidence_register"],
        "conditional_branch": "DEGRADE_IF_C0_FAIL",
        "hitl_trigger": "required_document_missing",
        "description": (
            "Reconcile submitted documents against EvidenceRegister. "
            "Requires evidence_refs from FinalEvidenceContract (C0 output). "
            "Short-circuits to DEGRADE when c0_state=FAIL and no required docs present."
        ),
    },
    {
        "stage_id": "stage_3_feature_derivation",
        "sequence": 3,
        "engine": "FeatureDerivationEngine",
        "l2_receipt": L2_RECEIPT_E3,
        "output_type": "RiskFeatures",
        "requires_evidence_refs": True,
        "depends_on": ["stage_2_document_reconciliation"],
        "conditional_branch": None,
        "hitl_trigger": None,
        "description": (
            "Derive risk features from reconciled evidence spans. "
            "Requires evidence_refs from Stage 2 ReconciliationResult. "
            "No new retrieval — all feature values come from extracted spans."
        ),
    },
    {
        "stage_id": "stage_4_risk_scoring",
        "sequence": 4,
        "engine": "RiskEvidenceScoringEngine",
        "l2_receipt": L2_RECEIPT_E3,
        "output_type": "RiskDimensionScores",
        "requires_evidence_refs": True,
        "depends_on": ["stage_3_feature_derivation"],
        "conditional_branch": None,
        "hitl_trigger": "borderline_score_band",
        "description": (
            "Score risk dimensions from derived features. "
            "Requires evidence_refs from Stage 3 RiskFeatures. "
            "Borderline score band [0.40, 0.55) triggers HITL_REQUIRED posture."
        ),
    },
    {
        "stage_id": "stage_5_decision_assembly",
        "sequence": 5,
        "engine": "DecisionPacketAssembler",
        "l2_receipt": L2_RECEIPT_E5,
        "output_type": "DecisionPacketCandidate",
        "requires_evidence_refs": True,
        "depends_on": ["stage_4_risk_scoring"],
        "conditional_branch": "CAVEAT_ENRICHMENT_IF_CONTRADICTION",
        "hitl_trigger": "contradiction_flags_present",
        "description": (
            "Seal the DecisionPacket artifact. "
            "Requires evidence_refs from Stage 4 RiskDimensionScores. "
            "Injects CAVEAT_ENRICHMENT branch when contradiction_flags present. "
            "PA compiler (LLM firewall) precedes any rationale generation."
        ),
    },
]


@dataclass
class WorkflowExpansion:
    """Expanded workflow graph for the underwriting R3R4_MANAGED_WORKFLOW.

    L3 EXPANDS — it does not execute. Stage execution is L2's responsibility.

    Fields:
      workflow_id: Canonical workflow identifier.
      route_family: Always R3R4_MANAGED_WORKFLOW.
      stage_count: Always 5.
      stages: List of stage contract dicts with dependency edges injected.
      l3_expanded: Always True after expand() completes.
      hitl_posture: HITL_REQUIRED | HITL_ADVISORY | HITL_NONE.
      hitl_triggers: List of triggered HITL rule IDs for observability.
      active_branches: List of conditional branch IDs active in this expansion.
      c0_state: c0_state from the run_context FEC, for branch resolution.
      evidence_refs: evidence_ids list from the FEC, required by Stages 2–5.
    """

    workflow_id: str = WORKFLOW_ID
    route_family: str = ROUTE_FAMILY
    stage_count: int = STAGE_COUNT
    stages: list[dict[str, Any]] = field(default_factory=lambda: list(STAGE_CONTRACTS))
    l3_expanded: bool = True
    hitl_posture: str = HITL_NONE
    hitl_triggers: list[str] = field(default_factory=list)
    active_branches: list[str] = field(default_factory=list)
    c0_state: str = ""
    evidence_refs: list[str] = field(default_factory=list)


def _resolve_hitl_posture(
    c0_state: str,
    contradiction_flags: list[str],
    missing_evidence_flags: list[str],
    support_score: float,
) -> tuple[str, list[str]]:
    """Determine HITL posture from C0 evidence contract fields.

    Returns (posture, triggers) where triggers lists every rule that fired.
    HITL_REQUIRED takes precedence over HITL_ADVISORY.
    """
    triggers: list[str] = []

    # HITL_REQUIRED triggers.
    if missing_evidence_flags:
        triggers.append("required_document_missing")
    if contradiction_flags:
        triggers.append("contradiction_flags_present")
    if c0_state == "FAIL":
        triggers.append("c0_state_fail_adverse")

    # HITL_ADVISORY triggers (borderline score band, no REQUIRED triggers yet).
    if not triggers and HITL_SCORE_FLOOR <= support_score < HITL_SCORE_CEILING:
        triggers.append("borderline_score_band")

    if any(t in triggers for t in (
        "required_document_missing",
        "contradiction_flags_present",
        "c0_state_fail_adverse",
    )):
        return HITL_REQUIRED, triggers
    if "borderline_score_band" in triggers:
        return HITL_ADVISORY, triggers
    return HITL_NONE, triggers


def _resolve_active_branches(
    c0_state: str,
    contradiction_flags: list[str],
    missing_evidence_flags: list[str],
) -> list[str]:
    """Determine which conditional branches are active for this expansion."""
    branches: list[str] = []
    if c0_state == "FAIL" and missing_evidence_flags:
        branches.append("DEGRADE_IF_C0_FAIL")
    if contradiction_flags:
        branches.append("CAVEAT_ENRICHMENT_IF_CONTRADICTION")
    return branches


class UnderwritingL3WorkflowAdapter:
    """Adapter that expands the five-stage underwriting workflow for L3.

    Invariants:
    - NEVER executes stages — declares the stage graph only
    - NEVER performs retrieval — reads FEC from run_context only
    - NEVER writes to L4 — expansion is a pure read operation
    - evidence_refs from FEC are threaded into all requires_evidence_refs stages
    - HITL posture is computed from FEC fields and injected into expansion
    """

    def expand(self, run_context: dict[str, Any]) -> WorkflowExpansion:
        """Expand the workflow graph from the run context.

        Reads the FinalEvidenceContract from run_context (populated by C0 pass),
        resolves HITL posture and conditional branches, and returns a fully
        declared WorkflowExpansion. Does NOT execute any stage.

        Args:
            run_context: Runtime context dict. Expected keys:
              - final_evidence_contract: FinalEvidenceContract dict or object
              - request_id: str (for tracing)
              - capability_id: str

        Returns:
            WorkflowExpansion with all five stage contracts, dependency edges,
            HITL posture, and active branches declared.
        """
        fec = run_context.get("final_evidence_contract") or {}
        if hasattr(fec, "to_dict"):
            fec = fec.to_dict()

        c0_state: str = fec.get("c0_state", "FAIL") if isinstance(fec, dict) else "FAIL"
        contradiction_flags: list[str] = (
            fec.get("contradiction_flags", []) if isinstance(fec, dict) else []
        )
        missing_evidence_flags: list[str] = (
            fec.get("missing_evidence_flags", []) if isinstance(fec, dict) else []
        )
        support_score: float = float(
            fec.get("support_score", 0.0) if isinstance(fec, dict) else 0.0
        )
        evidence_refs: list[str] = (
            fec.get("evidence_ids", []) if isinstance(fec, dict) else []
        )

        hitl_posture, hitl_triggers = _resolve_hitl_posture(
            c0_state=c0_state,
            contradiction_flags=contradiction_flags,
            missing_evidence_flags=missing_evidence_flags,
            support_score=support_score,
        )
        active_branches = _resolve_active_branches(
            c0_state=c0_state,
            contradiction_flags=contradiction_flags,
            missing_evidence_flags=missing_evidence_flags,
        )

        # Build stage list with evidence_refs injected into requires_evidence_refs stages.
        stages: list[dict[str, Any]] = []
        for contract in STAGE_CONTRACTS:
            stage = dict(contract)
            if stage["requires_evidence_refs"]:
                stage["injected_evidence_refs"] = list(evidence_refs)
            else:
                stage["injected_evidence_refs"] = []
            # Mark branch active/inactive in each stage.
            branch = stage.get("conditional_branch")
            stage["branch_active"] = branch in active_branches if branch else False
            stages.append(stage)

        return WorkflowExpansion(
            workflow_id=WORKFLOW_ID,
            route_family=ROUTE_FAMILY,
            stage_count=STAGE_COUNT,
            stages=stages,
            l3_expanded=True,
            hitl_posture=hitl_posture,
            hitl_triggers=hitl_triggers,
            active_branches=active_branches,
            c0_state=c0_state,
            evidence_refs=list(evidence_refs),
        )
