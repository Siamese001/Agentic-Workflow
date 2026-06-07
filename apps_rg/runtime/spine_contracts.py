"""Verified spine contract facade for apps_rg.

apps_rg code should import spine contract types through this module during the
lean-core migration. This facade re-exports only symbols verified in
docs/reports/apps_rg/apps_rg_contract_symbol_inventory.md.

Do not add aliases for missing contracts. Missing contracts require an explicit
spine owner decision or a clearly non-canonical app-local migration protocol.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition

__all__ = [
    "CompiledPromptArtifact",
    "FinalEvidenceContract",
    "GraphTraversePolicy",
    "L1PlanContract",
    "L3ToL2StepContract",
    "RouteContract",
    "SealedL2Artifact",
    "ValidatedRequest",
    "X3Disposition",
]
