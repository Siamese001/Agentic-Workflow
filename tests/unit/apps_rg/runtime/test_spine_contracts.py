from __future__ import annotations

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition

from apps_rg.runtime import spine_contracts


def test_spine_contracts_exports_only_verified_contract_symbols() -> None:
    assert set(spine_contracts.__all__) == {
        "CompiledPromptArtifact",
        "FinalEvidenceContract",
        "GraphTraversePolicy",
        "L1PlanContract",
        "L3ToL2StepContract",
        "RouteContract",
        "SealedL2Artifact",
        "ValidatedRequest",
        "X3Disposition",
    }


def test_spine_contracts_reexport_canonical_core_contracts() -> None:
    assert spine_contracts.CompiledPromptArtifact is CompiledPromptArtifact
    assert spine_contracts.FinalEvidenceContract is FinalEvidenceContract
    assert spine_contracts.GraphTraversePolicy is GraphTraversePolicy
    assert spine_contracts.L1PlanContract is L1PlanContract
    assert spine_contracts.L3ToL2StepContract is L3ToL2StepContract
    assert spine_contracts.RouteContract is RouteContract
    assert spine_contracts.SealedL2Artifact is SealedL2Artifact
    assert spine_contracts.ValidatedRequest is ValidatedRequest
    assert spine_contracts.X3Disposition is X3Disposition

