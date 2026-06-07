"""Verified apps_rg spine contract facade tests."""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    ValidatedRequest as CoreValidatedRequest,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact as CoreCompiledPromptArtifact,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract as CoreFinalEvidenceContract,
)
from agentic_core.runtime.contracts.l1_plan_contract import (
    L1PlanContract as CoreL1PlanContract,
)
from agentic_core.runtime.contracts.l3_to_l2_step_contract import (
    L3ToL2StepContract as CoreL3ToL2StepContract,
)
from agentic_core.runtime.contracts.route_contract import (
    GraphTraversePolicy as CoreGraphTraversePolicy,
)
from agentic_core.runtime.contracts.route_contract import RouteContract as CoreRouteContract
from agentic_core.runtime.contracts.sealed_l2_artifact import (
    SealedL2Artifact as CoreSealedL2Artifact,
)
from agentic_core.runtime.contracts.x3_disposition import (
    X3Disposition as CoreX3Disposition,
)

from apps_rg.runtime import spine_contracts


EXPECTED_EXPORTS = {
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

MISSING_CONTRACT_NAMES = {
    "CommitRequest",
    "ExitDispositionReceipt",
    "ExitReviewPacket",
    "RejectedRequest",
    "RuntimeExhaustBundle",
    "SealedSectionArtifact",
}


def test_spine_contracts_exports_only_verified_inventory_symbols() -> None:
    assert set(spine_contracts.__all__) == EXPECTED_EXPORTS


def test_spine_contracts_reexport_canonical_contract_objects() -> None:
    assert spine_contracts.ValidatedRequest is CoreValidatedRequest
    assert spine_contracts.L1PlanContract is CoreL1PlanContract
    assert spine_contracts.RouteContract is CoreRouteContract
    assert spine_contracts.GraphTraversePolicy is CoreGraphTraversePolicy
    assert spine_contracts.FinalEvidenceContract is CoreFinalEvidenceContract
    assert spine_contracts.CompiledPromptArtifact is CoreCompiledPromptArtifact
    assert spine_contracts.L3ToL2StepContract is CoreL3ToL2StepContract
    assert spine_contracts.SealedL2Artifact is CoreSealedL2Artifact
    assert spine_contracts.X3Disposition is CoreX3Disposition


def test_spine_contracts_has_no_missing_contract_placeholders() -> None:
    for name in MISSING_CONTRACT_NAMES:
        assert not hasattr(spine_contracts, name)


def test_spine_contracts_source_has_no_placeholder_assignments() -> None:
    source_path = Path(spine_contracts.__file__ or "")
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    assigned_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    assigned_names.add(target.id)
    assert assigned_names.isdisjoint(MISSING_CONTRACT_NAMES)
