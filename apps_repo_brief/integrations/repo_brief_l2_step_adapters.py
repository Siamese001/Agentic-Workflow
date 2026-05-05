"""L2 receipt type constants for apps_repo_brief managed workflow.

Three receipt types correspond to the three stages declared by
``RepoBriefL3WorkflowAdapter``:

  E1 — C0 Retrieval Bound         : C0 retrieval request validated + bound
  E2 — Evidence Validated         : PA evidence slots validated against FEC
  E3 — Artifact Sealed            : Exit-sealed repo-brief output artifact

Pattern source: apps_underwriting_ai.integrations.underwriting_l2_step_adapters

Plan: apps-repo-brief-l3-workflow-e2c7d9 P1.2
"""
from __future__ import annotations

L2_RECEIPT_E1 = "L2.E1.repo_brief_c0_context_bound"
L2_RECEIPT_E2 = "L2.E2.repo_brief_evidence_validated"
L2_RECEIPT_E3 = "L2.E3.repo_brief_artifact_sealed"

RECEIPT_STAGE_MAP: dict[str, int] = {
    L2_RECEIPT_E1: 1,
    L2_RECEIPT_E2: 2,
    L2_RECEIPT_E3: 3,
}

__all__ = [
    "L2_RECEIPT_E1",
    "L2_RECEIPT_E2",
    "L2_RECEIPT_E3",
    "RECEIPT_STAGE_MAP",
]
