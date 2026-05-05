"""L3 managed workflow adapter for apps_repo_brief.

Declares the three-stage workflow contract for R3_grounded_read.
L3 EXPANDS the workflow — it does NOT execute stages.

Three stages (linear dependency chain):
  Stage 1 — C0 Retrieval Bound        → L2.E1.repo_brief_c0_context_bound
  Stage 2 — Prompt Assembly Validated → L2.E2.repo_brief_evidence_validated
             (requires evidence_refs from Stage 1 output)
  Stage 3 — Exit Sealed               → L2.E3.repo_brief_artifact_sealed
             (requires evidence_refs from Stage 2 output)

HITL posture injection rules (mirrors underwriting adapter pattern):
  - c0_state=FAIL + no sources → HITL_REQUIRED
  - contradiction_flags present → HITL_ADVISORY
  - evidence_status=MISSING → HITL_REQUIRED
  - otherwise → HITL_NONE

Pattern source: apps_underwriting_ai.integrations.underwriting_l3_workflow_adapter
Plan: apps-repo-brief-l3-workflow-e2c7d9 P1.1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_repo_brief.integrations.repo_brief_l2_step_adapters import (
    L2_RECEIPT_E1,
    L2_RECEIPT_E2,
    L2_RECEIPT_E3,
)

WORKFLOW_ID = "repo_brief_grounded_read_v1"
ROUTE_FAMILY = "R3_grounded_read"
STAGE_COUNT = 3

HITL_REQUIRED = "HITL_REQUIRED"
HITL_ADVISORY = "HITL_ADVISORY"
HITL_NONE = "HITL_NONE"

STAGE_CONTRACTS: list[dict[str, Any]] = [
    {
        "stage_id": "stage_1_c0_retrieval_bound",
        "sequence": 1,
        "l2_receipt": L2_RECEIPT_E1,
        "output_type": "C0ContextBound",
        "requires_evidence_refs": False,
        "depends_on": [],
        "conditional_branch": None,
        "hitl_trigger": None,
        "description": (
            "Bind C0 retrieval context; validate C0RequestSpec against "
            "depth-profile thresholds."
        ),
    },
    {
        "stage_id": "stage_2_evidence_validated",
        "sequence": 2,
        "l2_receipt": L2_RECEIPT_E2,
        "output_type": "EvidenceValidated",
        "requires_evidence_refs": True,
        "depends_on": ["stage_1_c0_retrieval_bound"],
        "conditional_branch": None,
        "hitl_trigger": "contradiction_flags_present",
        "description": (
            "Validate PA evidence slots against FinalEvidenceContract sources. "
            "Requires evidence_refs from Stage 1."
        ),
    },
    {
        "stage_id": "stage_3_artifact_sealed",
        "sequence": 3,
        "l2_receipt": L2_RECEIPT_E3,
        "output_type": "RepoBriefArtifactSealed",
        "requires_evidence_refs": True,
        "depends_on": ["stage_2_evidence_validated"],
        "conditional_branch": None,
        "hitl_trigger": None,
        "description": (
            "Seal the repo-brief output artifact via Exit v6. "
            "Requires evidence_refs from Stage 2."
        ),
    },
]


@dataclass
class WorkflowExpansion:
    """Expanded workflow graph for apps_repo_brief R3_grounded_read.

    L3 EXPANDS — it does not execute. Stage execution is L2's responsibility.
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
    evidence_status: str,
) -> tuple[str, list[str]]:
    """Determine HITL posture from C0 FEC fields.

    HITL_REQUIRED takes precedence over HITL_ADVISORY.
    Returns (posture, triggers).
    """
    triggers: list[str] = []

    if c0_state == "FAIL":
        triggers.append("c0_state_fail")
    if evidence_status == "MISSING":
        triggers.append("evidence_status_missing")
    if contradiction_flags:
        triggers.append("contradiction_flags_present")

    required_triggers = {"c0_state_fail", "evidence_status_missing"}
    if any(t in required_triggers for t in triggers):
        return HITL_REQUIRED, triggers
    if "contradiction_flags_present" in triggers:
        return HITL_ADVISORY, triggers
    return HITL_NONE, triggers


class RepoBriefL3WorkflowAdapter:
    """Adapter that expands the three-stage repo-brief workflow for L3.

    Invariants:
    - NEVER executes stages — declares the stage graph only
    - NEVER performs retrieval — reads FEC from run_context only
    - NEVER writes to L4 — expansion is a pure read operation
    - NEVER mutates run_context
    """

    def expand(self, run_context: dict[str, Any]) -> WorkflowExpansion:
        """Expand the workflow graph from the run context.

        Reads C0 FEC state from run_context, resolves HITL posture,
        and returns a fully declared WorkflowExpansion. Does NOT execute
        any stage.

        Args:
            run_context: dict with optional keys:
              - c0_fec: dict from spine_handoff C0 seam
              - final_evidence_contract: alternative FEC key

        Returns:
            WorkflowExpansion with all three stage contracts, dependency
            edges, HITL posture, and evidence_refs injected.
        """
        fec: dict[str, Any] = {}
        c0_fec = run_context.get("c0_fec")
        if isinstance(c0_fec, dict):
            fec = c0_fec
        elif isinstance(run_context.get("final_evidence_contract"), dict):
            fec = run_context["final_evidence_contract"]

        c0_state: str = fec.get("c0_state", "FAIL") if fec else "FAIL"
        contradiction_flags: list[str] = fec.get("contradiction_flags", []) if fec else []
        evidence_status: str = fec.get("evidence_status", "MISSING") if fec else "MISSING"
        evidence_refs: list[str] = fec.get("evidence_ids", []) if fec else []

        hitl_posture, hitl_triggers = _resolve_hitl_posture(
            c0_state=c0_state,
            contradiction_flags=contradiction_flags,
            evidence_status=evidence_status,
        )

        stages: list[dict[str, Any]] = []
        for contract in STAGE_CONTRACTS:
            stage = dict(contract)
            stage["injected_evidence_refs"] = list(evidence_refs) if stage["requires_evidence_refs"] else []
            stages.append(stage)

        return WorkflowExpansion(
            workflow_id=WORKFLOW_ID,
            route_family=ROUTE_FAMILY,
            stage_count=STAGE_COUNT,
            stages=stages,
            l3_expanded=True,
            hitl_posture=hitl_posture,
            hitl_triggers=hitl_triggers,
            active_branches=[],
            c0_state=c0_state,
            evidence_refs=list(evidence_refs),
        )


__all__ = [
    "WORKFLOW_ID",
    "ROUTE_FAMILY",
    "STAGE_COUNT",
    "STAGE_CONTRACTS",
    "HITL_REQUIRED",
    "HITL_ADVISORY",
    "HITL_NONE",
    "WorkflowExpansion",
    "RepoBriefL3WorkflowAdapter",
]
