"""Contract bundles for section runs.

``SectionFrontSpineBridge`` contains only U0/L1/L0 contracts plus execution
context. ``SectionRunContractBundle`` carries downstream C0/PA/L2/Exit runtime
contracts so section debugging does not turn the front bridge into a mini-spine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.section_spine_terminology import CANONICAL_CONTRACT_TYPES
from apps_rg.runtime.spine_contracts import (
    CompiledPromptArtifact,
    FinalEvidenceContract,
    L1PlanContract,
    RouteContract,
    SealedL2Artifact,
    ValidatedRequest,
    X3Disposition,
)

FRONT_SPINE_CONTRACTS: tuple[str, ...] = (
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
)

DOWNSTREAM_MISSING_CANONICAL_CONTRACTS: tuple[str, ...] = tuple(
    c for c in CANONICAL_CONTRACT_TYPES if c not in FRONT_SPINE_CONTRACTS
)

OBSERVED_CHAIN_WITH_FRONT_BRIDGE: tuple[str, ...] = (
    "CLI",
    "section_front_spine_bridge",
    "U0",
    "L1",
    "L0",
    "proof_pool_resolver",
    "section_lane_modular",
)


@dataclass(frozen=True, slots=True)
class SectionFrontSpineBridge:
    """Front-spine contract bundle for a section lane invocation."""

    section_id: str
    validated_request: ValidatedRequest | None
    l1_plan: L1PlanContract | None
    route: RouteContract | None
    product_visible: bool = True
    fixture_dev_only_bypass: bool = False
    non_product_certified: bool = False
    observed_chain: tuple[str, ...] = OBSERVED_CHAIN_WITH_FRONT_BRIDGE
    missing_downstream_contracts: tuple[str, ...] = DOWNSTREAM_MISSING_CANONICAL_CONTRACTS
    spine_lane_mode: str = "section_spine_run"
    is_canonical_c0_path: bool = False
    whole_run_envelope: bool = False

    def contracts_emitted(self) -> dict[str, bool]:
        return {
            "ValidatedRequest": self.validated_request is not None,
            "L1PlanContract": self.l1_plan is not None,
            "RouteContract": self.route is not None,
        }


@dataclass(frozen=True, slots=True)
class SectionRunContractBundle:
    """Downstream contract bundle for section lane runtime."""

    evidence_contract: FinalEvidenceContract | None = None
    compiled_prompt: CompiledPromptArtifact | None = None
    sealed_artifact: SealedL2Artifact | None = None
    section_exit_receipt: Any | None = None
    x3_disposition: X3Disposition | None = None

    def contracts_emitted(self) -> dict[str, bool]:
        return {
            "FinalEvidenceContract": self.evidence_contract is not None,
            "CompiledPromptArtifact": self.compiled_prompt is not None,
            "SealedL2Artifact": self.sealed_artifact is not None,
            "ExitDispositionReceipt": self.section_exit_receipt is not None,
            "X3Disposition": self.x3_disposition is not None,
        }

    def runtime_complete(self) -> bool:
        """True when section C0, PA, L2, and Exit receipt are present."""
        emitted = self.contracts_emitted()
        return all(
            emitted[name]
            for name in (
                "FinalEvidenceContract",
                "CompiledPromptArtifact",
                "SealedL2Artifact",
                "ExitDispositionReceipt",
            )
        )


__all__ = [
    "DOWNSTREAM_MISSING_CANONICAL_CONTRACTS",
    "FRONT_SPINE_CONTRACTS",
    "OBSERVED_CHAIN_WITH_FRONT_BRIDGE",
    "SectionFrontSpineBridge",
    "SectionRunContractBundle",
]
